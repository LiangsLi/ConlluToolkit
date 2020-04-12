# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
import re
import json
import pathlib
import random
from pprint import pprint
from typing import List, Tuple, Any, Callable, Union, Optional, Dict
from conllu import parse, parse_incr, TokenList
from conlluprocessor.base import load, save, is_conllu_data, check_or_load
from conlluprocessor.statistic import statistics
from conlluprocessor.convert import sdp_to_conllu, conllu_to_sdp
from conlluprocessor.type import CONLLUDataOrPath, CONLLUData


def process(input_conllu_data_or_file: CONLLUDataOrPath,
            process_fn: Callable[[TokenList], Any],
            output_conllu_file: str = None,
            strict: bool = True):
    input_conllu_data = check_or_load(input_conllu_data_or_file, strict)
    output_result = []
    for sentence in input_conllu_data:
        output_sentence = process_fn(sentence)
        if output_sentence:
            output_result.append(output_sentence)
    if output_conllu_file and is_conllu_data(output_result):
        save(output_result, output_conllu_file)
    return output_result


def find_pattern(conllu_data_or_file: CONLLUDataOrPath,
                 output_file: str,
                 pattern: str) -> None:
    """
    依据正则在conllu数据或者文件中查询句子
    只匹配句子形式

    Args:
        conllu_data_or_file: 查询的conllu数据或者文件
        output_file: 查询结果输出文件
        pattern: 合法的正则模式

    Returns:
        无返回值
    """
    def find_fun(_sentence: TokenList) -> Optional[TokenList]:
        _sentence_str = ''.join(t['form'] for t in _sentence)
        if re.findall(pattern, _sentence_str):
            return _sentence
        else:
            return None

    search_result = process(conllu_data_or_file, process_fn=find_fun, strict=True)
    with open(output_file, 'w', encoding='utf-8')as f:
        f.write(f'# Search {pattern}\n')
        f.write(f'# {len(search_result)} sentences found\n\n')
        for i, sentence in enumerate(search_result):
            f.write(f'### {i + 1}\n')
            f.write(sentence.serialize())


def find_dependency(conllu_data_or_file: CONLLUDataOrPath,
                    output_file: str,
                    head_word: str = None,
                    head_pos: str = None,
                    deprel: str = None,
                    dependent_word: str = None,
                    dependent_pos: str = None) -> None:
    """
    依据依存条件在conllu数据或者文件中查找句子
    这里支持的依存条件为：头节点单词、头节点词性、尾节点单词、尾节点词性、依存标签，以上条件可为空，但是至少有一个不为空

    Args:
        conllu_data_or_file: 查询的conllu数据或者文件
        output_file: 查询结果输出文件
        head_word: 头节点单词
        head_pos: 头节点词性
        deprel: 依存标签
        dependent_word: 尾节点单词
        dependent_pos: 尾节点词性

    Returns:
        无返回值
    """
    if not any([head_word, head_pos, deprel, dependent_word, dependent_pos]):
        raise RuntimeError('至少需要指定一个查询条件[head_word, head_pos, deprel, dependent_word, dependent_pos]')

    def find_fun(_sentence: TokenList) -> Optional[Tuple[List, TokenList]]:
        sentence_search_result = []
        for token in _sentence:
            if dependent_word and token['form'] != dependent_word:
                continue
            if dependent_pos and token['upostag'] != dependent_pos:
                continue
            for dep_label, head_id in token['deps']:
                if head_word and _sentence[head_id - 1]['form'] != head_word:
                    continue
                if head_pos and _sentence[head_id - 1]['upostag'] != head_pos:
                    continue
                if dep_label == deprel:
                    sentence_search_result.append(
                        f"### ({head_id},{_sentence[head_id - 1]['form']},{_sentence[head_id - 1]['upostag']})"
                        f" --{deprel}-> "
                        f"({token['id']},{token['form']},{token['upostag']})"
                    )
        if sentence_search_result:
            return sentence_search_result, _sentence
        else:
            return None

    search_result = process(conllu_data_or_file, process_fn=find_fun, strict=True)
    with open(output_file, 'w', encoding='utf-8')as f:
        f.write(f'# Search [{head_word},{head_pos}] --{deprel}-> [{dependent_word},{dependent_pos}]\n')
        f.write(f'# {len(search_result)} sentences found\n\n')
        for i, (patterns, sentence) in enumerate(search_result):
            f.write(f'### {i + 1}\n')
            f.writelines('\n'.join(patterns) + '\n')
            f.write(sentence.serialize())


def diff(conllu_data_or_file_a: CONLLUDataOrPath,
         conllu_data_or_file_b: CONLLUDataOrPath,
         output_file: str,
         strict: bool = True,
         ignore_root_id: bool = True,
         ignore_case: bool = True,
         ignore_pos: bool = False) -> None:
    """
    比较两个conllu文件或者数据，并输出不同
    不同于原始的diff，这里比较的时候无视句子的顺利，而且以句子为单位比较

    Args:
        conllu_data_or_file_a: conllu数据或者文件a
        conllu_data_or_file_b: conllu数据或者文件b
        output_file: 比较结果的输出文件
        strict: 是否要求是严格的conllu文件
        ignore_root_id: 是否无视ROOT的根节点序号差异
        ignore_case: 是否无视依存标签的大小写差异
        ignore_pos: 是否无视词性的差异

    Returns:
        无返回值
    """
    data_a, data_b = check_or_load(conllu_data_or_file_a, strict), check_or_load(conllu_data_or_file_b, strict)

    def convert2sentence2token_list(data: CONLLUData) -> Dict[str, TokenList]:
        _result = {}
        for _sentence in data:
            _sentence_str = ''.join([token['form'] for token in _sentence])
            _result[_sentence_str] = _sentence
        return _result

    def diff_sentence(_sentence_a: TokenList, _sentence_b: TokenList) -> Dict[str, List]:
        _id2diff = {}

        def deps2dict(_deps: List[Tuple[str, int]]) -> Dict[str, int]:
            _d = {}
            for _rel, _id in _deps:
                if ignore_case:
                    _rel = _rel.lower()
                _d[_rel] = _id
            return _d

        for t_a, t_b in zip(_sentence_a, _sentence_b):
            diff_items = []
            if t_a['form'] != t_b['form']:
                diff_items.append('form')
            if t_a['upostag'] != t_b['upostag'] and not ignore_pos:
                diff_items.append('upostag')
            t_a_deps = deps2dict(t_a['deps'])
            t_b_deps = deps2dict(t_b['deps'])
            if len(set(t_a_deps.keys()) - set(t_b_deps.keys())) > 0:
                diff_items.append('deps')
            else:
                for rel in t_a_deps:
                    if rel == 'root' and ignore_root_id:
                        continue
                    if t_a_deps[rel] != t_b_deps[rel]:
                        diff_items.append('deps')
                        break
            if diff_items:
                _id2diff[str(t_a['id'])] = diff_items
        return _id2diff

    data_a, data_b = convert2sentence2token_list(data_a), convert2sentence2token_list(data_b)
    only_in_a = set(data_a.keys()) - set(data_b.keys())
    only_in_b = set(data_b.keys()) - set(data_a.keys())
    both_in_a_and_b = set(data_b.keys()) & set(data_a.keys())
    difference = []
    for sentence in both_in_a_and_b:
        if data_a[sentence] != data_b[sentence]:
            difference.append(sentence)

    with open(output_file, 'w', encoding='utf-8')as f:
        f.write('# Diff result:\n')
        f.write(f'# a sentence num:{len(data_a)}\n')
        f.write(f'# b sentence num:{len(data_b)}\n')
        f.write(f'# only in a:{len(only_in_a)}\n')
        f.write(f'# Only in b:{len(only_in_b)}\n')
        f.write(f'# difference in a and b:{len(difference)}\n\n')
        f.write('###' * 10 + '\n')
        for i, oa in enumerate(only_in_a):
            f.write(f'### [only in a] No.{i + 1} {oa}\n')
            f.write(data_a[oa].serialize())
        f.write('###' * 10 + '\n')
        for i, ob in enumerate(only_in_b):
            f.write(f'### [only in b] No.{i + 1} {ob}\n')
            f.write(data_b[ob].serialize())
        f.write('###' * 10 + '\n')
        i = 1
        for d in difference:
            diffs = diff_sentence(data_a[d], data_b[d])
            if diffs:
                f.write(f'### [difference] No.{i} {d}\n')
                a_strs = data_a[d].serialize().split('\n')
                b_strs = data_b[d].serialize().split('\n')
                for j, a_s in enumerate(a_strs):
                    f.write(a_s + '\n')
                    if str(j + 1) in diffs:
                        f.write(f'## difference in b:{diffs[str(j + 1)]}\n')
                        f.write('##' + b_strs[j] + '\n')
                i += 1


def split_date_set(conllu_data_or_file: CONLLUDataOrPath,
                   train: Union[int, float], dev: Union[int, float, None], test: Union[int, float],
                   output_dir: str, shuffle: bool = True, strict: bool = True) -> Tuple:
    """
    按照比例或者数量切分数据集，结果写入文件同时返回

    Args:
        conllu_data_or_file: 等待切分的conllu数据或者文件路径
        train: 训练集大小（数量或者比例）
        dev: 验证集大小（数量或者比例）
        test: 测试集大小（数量或者比例）
        output_dir: 输出文件的文件夹路径
        shuffle: 切分前是否打乱顺利
        strict: 是否要求输入数据是必须是conllu（如False则支持semeval16的原始数据格式）

    Returns:
        返回切分后的训练集、验证集、测试集数据
    """
    if not pathlib.Path(output_dir).is_dir():
        raise RuntimeError(f'output_dir({output_dir} is not dir)')
    conllu_data = check_or_load(conllu_data_or_file, strict)
    sentence_num = len(conllu_data)
    if train == 0 or test == 0:
        raise RuntimeError('train和test数量不能为0')
    if 0 < train < 1:
        if dev > 1 or test > 1:
            raise RuntimeError('如果train为比例，则dev和test都必须为比例')
        if (dev + train + test) != 1:
            raise RuntimeError('比例之和必须为1')
        is_ratio = True
    if train >= 1:
        if train % 1 != 0 or dev % 1 != 0 or test % 1 != 0:
            raise RuntimeError('数量只能为整数')
        if (train + dev + test) != sentence_num:
            raise RuntimeError(f'数量之和必须等于总句子数({sentence_num})')
        is_ratio = False
    if is_ratio:
        train_data_num = int(sentence_num * train)
        dev_data_num = int(sentence_num * dev)
    else:
        train_data_num = int(train)
        dev_data_num = int(dev)
    if shuffle:
        random.shuffle(conllu_data)
    train_data = conllu_data[:train_data_num]
    dev_data = conllu_data[train_data_num:train_data_num + dev_data_num]
    test_data = conllu_data[train_data_num + dev_data_num:]
    output_dir = pathlib.Path(output_dir)
    if len(train_data) > 0:
        save(train_data, str(output_dir / f'train.{len(train_data)}.conllu'))
    if len(dev_data) > 0:
        save(dev_data, str(output_dir / f'dev.{len(dev_data)}.conllu'))
    if len(test_data) > 0:
        save(test_data, str(output_dir / f'test.{len(train_data)}.conllu'))
    return train_data, dev_data, test_data


if __name__ == '__main__':
    pass

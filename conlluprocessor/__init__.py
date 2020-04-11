# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
import json
import pathlib
import random
from pprint import pprint
from typing import List, Tuple
from conllu import parse, parse_incr, TokenList
from conlluprocessor.base import load, save, is_conllu_data, check_or_load
from conlluprocessor.statistic import statistics
from conlluprocessor.convert import sdp_to_conllu, conllu_to_sdp


def process(input_conllu_data_or_file, process_fn, output_conllu_file=None, strict=True):
    input_conllu_data = check_or_load(input_conllu_data_or_file, strict)
    output_result = []
    for sentence in input_conllu_data:
        output_sentence = process_fn(sentence)
        if output_sentence:
            output_result.append(output_sentence)
    if output_conllu_file and is_conllu_data(output_result):
        save(output_result, output_conllu_file)
    return output_result


def search(conllu_data_or_file, output_file, head_word=None, head_pos=None, deprel=None, dependent_word=None,
           dependent_pos=None):
    def search_fun(sentence) -> Tuple[List, TokenList]:
        sentence_search_result = []
        for token in sentence:
            if dependent_word and token['form'] != dependent_word:
                continue
            if dependent_pos and token['upostag'] != dependent_pos:
                continue
            for dep_label, head_id in token['deps']:
                if head_word and sentence[head_id - 1]['form'] != head_word:
                    continue
                if head_pos and sentence[head_id - 1]['upostag'] != head_pos:
                    continue
                if dep_label == deprel:
                    sentence_search_result.append(
                        f"### ({head_id},{sentence[head_id - 1]['form']},{sentence[head_id - 1]['upostag']})"
                        f" --{deprel}-> "
                        f"({token['id']},{token['form']},{token['upostag']})"
                    )
        if sentence_search_result:
            return sentence_search_result, sentence
        else:
            return None

    search_result = process(conllu_data_or_file, process_fn=search_fun, strict=True)
    with open(output_file, 'w', encoding='utf-8')as f:
        f.write(f'# Search [{head_word},{head_pos}] --{deprel}-> [{dependent_word},{dependent_pos}]\n')
        f.write(f'# {len(search_result)} sentences found\n\n')
        for i, (patterns, sentence) in enumerate(search_result):
            f.write(f'### {i + 1}\n')
            f.writelines('\n'.join(patterns) + '\n')
            f.write(sentence.serialize())


def diff(conllu_data_or_file_a, conllu_data_or_file_b,
         output_file, strict=True,
         ignore_root_id=True, ignore_case=True,
         ignore_pos=False):
    data_a, data_b = check_or_load(conllu_data_or_file_a, strict), check_or_load(conllu_data_or_file_b, strict)

    def convert2sentence2token_list(data):
        result = {}
        for sentence in data:
            sentence_str = ''.join([token['form'] for token in sentence])
            result[sentence_str] = sentence
        return result

    def diff_sentence(sentence_a, sentence_b):
        id2diff = {}

        def deps2dict(deps):
            _d = {}
            for _rel, _id in deps:
                if ignore_case:
                    _rel = _rel.lower()
                _d[_rel] = _id
            return _d

        for t_a, t_b in zip(sentence_a, sentence_b):
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
                id2diff[str(t_a['id'])] = diff_items
        return id2diff

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


def split_date_set(conllu_data_or_file, train, dev, test, output_dir, shuffle=True, strict=True):
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

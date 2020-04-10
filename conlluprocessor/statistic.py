# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
import json
import pathlib
from pprint import pprint
from typing import List, Tuple
from conllu import parse, parse_incr, TokenList


def statistic_non_projective(sentence_dep_pairs: List[Tuple[int, int]]):
    """
    统计传入的依存序号列表中是否存在非投射现象，以及非投射的数量
    :param sentence_dep_pairs: List[Tuple[int]]
    :return:
    """
    non_projective_pairs = []
    for i in range(len(sentence_dep_pairs)):
        for j in range(i + 1, len(sentence_dep_pairs)):
            if sentence_dep_pairs[i][0] < sentence_dep_pairs[j][0]:
                pair_a, pair_b = sentence_dep_pairs[i], sentence_dep_pairs[j]
            else:
                pair_a, pair_b = sentence_dep_pairs[j], sentence_dep_pairs[i]
            if pair_a[0] < pair_b[0] < pair_a[1] < pair_b[1]:
                non_projective_pairs.append((pair_a, pair_b))
    return len(non_projective_pairs), non_projective_pairs


def statistics(conllu_data: List[TokenList]):
    """
    统计传入的conllu data（使用conllu模块加载）
    conllu模块:https://github.com/EmilStenstrom/conllu
    :param conllu_data: List[TokenList] conllu数据
    :return: tuple：(result:Str, token_vocab:Counter, label_vocab:Counter) 统计结果；词表；依存标签表
    """
    from collections import Counter
    token_vocab = Counter()
    label_vocab = Counter()
    sentences_num = len(conllu_data)
    token_num = 0
    dependency_arc_num = 0
    multi_head_node_num = 0
    non_projective_num = 0
    for sentence in conllu_data:
        token_num += len(sentence)
        sentence_deps = []
        for token in sentence:
            dependency_arc_num += len(token['deps'])
            # 多父节点
            if len(token['deps']) > 1:
                multi_head_node_num += 1
            for dep in token['deps']:
                # token['deps']:
                #   [('mPrep', 5),(...)]
                sentence_deps.append((token['id'], dep[1]) if dep[1] > token['id'] else (dep[1], token['id']))
                label_vocab[dep[0]] += 1
            token_vocab[token['form']] += 1
        non_projective_num += statistic_non_projective(sentence_deps)[0]
    result = "---statistics result---\n"
    result += f'Sentence num:{sentences_num}\n'
    result += f'Average sentence length:{token_num / sentences_num:0.3f}\n'
    result += f'Dependency arc num:{dependency_arc_num}; {dependency_arc_num / sentences_num:0.3f} per sentence\n'
    result += f'Multi head num:{multi_head_node_num}; {multi_head_node_num / sentences_num:0.3f} per sentence\n'
    result += f'Non-projective num:{non_projective_num}; {non_projective_num / sentences_num:0.3f} per sentence\n'
    result += f'Token Vocab size:{len(token_vocab)}\n'
    result += f'Label Vocab size:{len(label_vocab)}\n'
    return result, token_vocab, label_vocab


if __name__ == '__main__':
    pass

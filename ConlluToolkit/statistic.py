# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
import json
import pathlib
from pprint import pprint
from collections import Counter
from typing import List, Tuple
from conllu import parse, parse_incr, TokenList
from .base import check_or_load
from .type import CONLLUData, CONLLUDataOrPath


def statistics(conllu_data_or_file: CONLLUDataOrPath) -> Tuple[str, Counter, Counter]:
    """
    统计

    Args:
        conllu_data_or_file: conllu数据或者文件路径

    Returns:
        返回统计信息字符串，词表，依存标签表
    """
    conllu_data = check_or_load(conllu_data_or_file)

    def statistic_non_projective(_sentence_dep_pairs: List[Tuple[int, int]]):
        """统计传入的依存序号列表中是否存在非投射现象，以及非投射的数量
        """
        non_projective_pairs = []
        for i in range(len(_sentence_dep_pairs)):
            for j in range(i + 1, len(_sentence_dep_pairs)):
                if _sentence_dep_pairs[i][0] < _sentence_dep_pairs[j][0]:
                    pair_a, pair_b = _sentence_dep_pairs[i], _sentence_dep_pairs[j]
                else:
                    pair_a, pair_b = _sentence_dep_pairs[j], _sentence_dep_pairs[i]
                if pair_a[0] < pair_b[0] < pair_a[1] < pair_b[1]:
                    non_projective_pairs.append((pair_a, pair_b))
        return len(non_projective_pairs), non_projective_pairs

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

# Created by li huayong on 2020/4/10
import typing
from collections import Counter
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from conllu import TokenList

from .base import check_or_load
from .type import CONLLUData
from .type import CONLLUDataOrPath


def statistics(conllu_data_or_file: CONLLUDataOrPath) -> Tuple[str, Counter, Counter]:
    """
    统计

    Args:
        conllu_data_or_file: conllu数据或者文件路径

    Returns:
        返回统计信息字符串，词表，依存标签表
    """
    conllu_data = check_or_load(conllu_data_or_file)

    def statistic_non_projective(
        _sentence_dep_pairs: List[Tuple[int, int]]
    ) -> Tuple[int, List]:
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

    token_vocab: typing.Counter = Counter()
    label_vocab: typing.Counter = Counter()
    sentences_num = len(conllu_data)
    token_num = 0
    dependency_arc_num = 0
    multi_head_node_num = 0
    non_projective_num = 0
    for sentence in conllu_data:
        token_num += len(sentence)
        sentence_deps = []
        for token in sentence:
            dependency_arc_num += len(token["deps"])
            # 多父节点
            if len(token["deps"]) > 1:
                multi_head_node_num += 1
            for dep in token["deps"]:
                # token['deps']:
                #   [('mPrep', 5),(...)]
                sentence_deps.append(
                    (token["id"], dep[1])
                    if dep[1] > token["id"]
                    else (dep[1], token["id"])
                )
                label_vocab[dep[0]] += 1
            token_vocab[token["form"]] += 1
        non_projective_num += statistic_non_projective(sentence_deps)[0]
    result = "---statistics result---\n"
    result += f"Sentence num:{sentences_num}\n"
    result += f"Average sentence length:{token_num / sentences_num:0.3f}\n"
    result += f"Dependency arc num:{dependency_arc_num}; {dependency_arc_num / sentences_num:0.3f} per sentence\n"
    result += f"Multi head num:{multi_head_node_num}; {multi_head_node_num / sentences_num:0.3f} per sentence\n"
    result += f"Non-projective num:{non_projective_num}; {non_projective_num / sentences_num:0.3f} per sentence\n"
    result += f"Token Vocab size:{len(token_vocab)}\n"
    result += f"Label Vocab size:{len(label_vocab)}\n"
    return result, token_vocab, label_vocab


def diff(  # noqa: C901
    conllu_data_or_file_a: CONLLUDataOrPath,
    conllu_data_or_file_b: CONLLUDataOrPath,
    output_file: str,
    strict: bool = True,
    ignore_root_id: bool = True,
    ignore_case: bool = True,
    ignore_pos: bool = False,
) -> None:
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
    data_a: Any = check_or_load(conllu_data_or_file_a, strict)
    data_b: Any = check_or_load(conllu_data_or_file_b, strict)

    def convert2sentence2token_list(data: CONLLUData) -> Dict[str, TokenList]:
        _result = {}
        for _sentence in data:
            _sentence_str = "".join([token["form"] for token in _sentence])
            _result[_sentence_str] = _sentence
        return _result

    def diff_sentence(
        _sentence_a: TokenList, _sentence_b: TokenList
    ) -> Dict[str, List]:
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
            if t_a["form"] != t_b["form"]:
                diff_items.append("form")
            if t_a["upostag"] != t_b["upostag"] and not ignore_pos:
                diff_items.append("upostag")
            t_a_deps = deps2dict(t_a["deps"])
            t_b_deps = deps2dict(t_b["deps"])
            if len(set(t_a_deps.keys()) - set(t_b_deps.keys())) > 0:
                diff_items.append("deps")
            else:
                for rel in t_a_deps:
                    if rel == "root" and ignore_root_id:
                        continue
                    if t_a_deps[rel] != t_b_deps[rel]:
                        diff_items.append("deps")
                        break
            if diff_items:
                _id2diff[str(t_a["id"])] = diff_items
        return _id2diff

    data_a, data_b = (
        convert2sentence2token_list(data_a),
        convert2sentence2token_list(data_b),
    )
    only_in_a = set(data_a.keys()) - set(data_b.keys())
    only_in_b = set(data_b.keys()) - set(data_a.keys())
    both_in_a_and_b = set(data_b.keys()) & set(data_a.keys())
    difference = []
    for sentence in both_in_a_and_b:
        if data_a[sentence] != data_b[sentence]:
            difference.append(sentence)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Diff result:\n")
        f.write(f"# a sentence num:{len(data_a)}\n")
        f.write(f"# b sentence num:{len(data_b)}\n")
        f.write(f"# only in a:{len(only_in_a)}\n")
        f.write(f"# Only in b:{len(only_in_b)}\n")
        f.write(f"# difference in a and b:{len(difference)}\n\n")
        f.write("###" * 10 + "\n")
        for i, oa in enumerate(only_in_a):
            f.write(f"### [only in a] No.{i + 1} {oa}\n")
            f.write(data_a[oa].serialize())
        f.write("###" * 10 + "\n")
        for i, ob in enumerate(only_in_b):
            f.write(f"### [only in b] No.{i + 1} {ob}\n")
            f.write(data_b[ob].serialize())
        f.write("###" * 10 + "\n")
        i = 1
        for d in difference:
            diffs = diff_sentence(data_a[d], data_b[d])
            if diffs:
                f.write(f"### [difference] No.{i} {d}\n")
                a_strs = data_a[d].serialize().split("\n")
                b_strs = data_b[d].serialize().split("\n")
                for j, a_s in enumerate(a_strs):
                    f.write(a_s + "\n")
                    if str(j + 1) in diffs:
                        f.write(f"## difference in b:{diffs[str(j + 1)]}\n")
                        f.write("##" + b_strs[j] + "\n")
                i += 1


if __name__ == "__main__":
    pass

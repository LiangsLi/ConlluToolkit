# flake8: noqa
# mypy: ignore-errors
# =========================================
# conlluToolkit-find_compound_noun
# Created by li huayong on 2020/5/27
# =========================================
import sys

sys.path.append("..")
from conllutoolkit.type import CONLLUDataOrPath
from conllu import TokenList
from conllutoolkit.base import process
import typing
import json
from pathlib import Path

try:
    from typing import Final
except ImportError:
    from typing_extensions import Final

POS_RULES: Final = [
    ["n", "n", "v"],
    ["n", "v", "v"],
    ["v", "n", "v"],
    ["n", "n", "n"],
    ["v", "n", "n"],
    ["n", "v", "n"],
]
# dependency rules:
# 3 -> 2 -> 1
# 3 -> 2 ; 3 -> 1 ; 1 2没有其他入弧,也没有出弧


def find_noun(
    conllu_data_or_file: CONLLUDataOrPath, output_json_file: str = None
) -> typing.List:
    def find_fun(_sentence: TokenList) -> typing.List:
        # One line in conllu:
        # OrderedDict([('id', 1),
        #              ('form', '村'),
        #              ('lemma', '村'),
        #              ('upostag', 'NN'),
        #              ('xpostag', 'NN'),
        #              ('feats', None),
        #              ('head', 4),
        #              ('deprel', 'LOC'),
        #              ('deps', [('LOC', 4)]),
        #              ('misc', None)])

        def check_deps(child_dict, parent_dict, only_one_parent, no_child=False):
            if no_child:
                for _token in _sentence:
                    for _token_dep in _token["deps"]:
                        if _token_dep[1] == child_dict["id"]:
                            return False
            if only_one_parent and len(child_dict["deps"]) > 1:
                return False
            for dep in child_dict["deps"]:
                if parent_dict["id"] == dep[1]:
                    return True
            return False

        if len(_sentence) < 3:
            # 小于三个词语的句子自动跳过
            return None
        _slices = []
        for _i in range(len(_sentence) - 3):
            _slices.append(_sentence[_i : _i + 3])
        _result = []
        for _slice in _slices:
            # 这里做了简化,只取得POS的小写的首个字母(忽视了北大POS和LTP POS的差异),
            # 注意这样可能导致一些错误,更好的方法是全部转化为ltp POS集合后处理
            _slice_pos = [_t["upostag"].lower()[0] for _t in _slice]
            if _slice_pos not in POS_RULES:
                # 首先检查词性是够满足条件
                continue
            if check_deps(_slice[1], _slice[2], only_one_parent=False) and check_deps(
                _slice[0], _slice[1], only_one_parent=False
            ):
                _result.append(
                    {"tokenlist": _slice, "pos": _slice_pos, "rule": "3->2->1",}
                )
            elif check_deps(
                _slice[0], _slice[2], only_one_parent=True, no_child=True
            ) and check_deps(_slice[1], _slice[2], only_one_parent=True, no_child=True):
                _result.append(
                    {
                        "tokenlist": _slice,
                        "pos": _slice_pos,
                        "rule": "3->2;3->1;one parent;no child",
                    }
                )
        return _result

    search_result = process(conllu_data_or_file, process_fn=find_fun, strict=True)
    if output_json_file is not None:
        with open(output_json_file, "w", encoding="utf-8") as f:
            json.dump(search_result, f, ensure_ascii=False, indent=2)
    return search_result


if __name__ == "__main__":
    fpd = "/home/liangs/MyCodes/doing_codes/CSDP_Biaffine_Parser_lhy/CSDP_Biaffine_Parser_lhy/dataset/medical3000/"
    result = []
    for file in Path(fpd).glob("*/*.conllu"):
        # print(file.name)
        result.extend(find_noun(str(file)))
    with open("./tmp/noun.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

# =========================================
# conlluToolkit-find
# Created by li huayong on 2020/5/12
# =========================================
import re
from typing import List
from typing import Optional
from typing import Tuple

from conllu import TokenList

from .base import process
from .type import CONLLUDataOrPath


def find_pattern(
    conllu_data_or_file: CONLLUDataOrPath, output_file: str, pattern: str
) -> None:
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
        _sentence_str = "".join(t["form"] for t in _sentence)
        if re.findall(pattern, _sentence_str):
            return _sentence
        else:
            return None

    search_result = process(conllu_data_or_file, process_fn=find_fun, strict=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Search {pattern}\n")
        f.write(f"# {len(search_result)} sentences found\n\n")
        for i, sentence in enumerate(search_result):
            f.write(f"### {i + 1}\n")
            f.write(sentence.serialize())


def find_dependency(  # noqa C901
    conllu_data_or_file: CONLLUDataOrPath,
    output_file: str,
    head_word: str = None,
    head_pos: str = None,
    deprel: str = None,
    dependent_word: str = None,
    dependent_pos: str = None,
) -> None:
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
        raise RuntimeError(
            "至少需要指定一个查询条件[head_word, head_pos, deprel, dependent_word, dependent_pos]"
        )

    def find_fun(_sentence: TokenList) -> Optional[Tuple[List, TokenList]]:
        sentence_search_result = []
        for token in _sentence:
            if dependent_word and token["form"] != dependent_word:
                continue
            if dependent_pos and token["upostag"] != dependent_pos:
                continue
            for dep_label, head_id in token["deps"]:
                if head_word and _sentence[head_id - 1]["form"] != head_word:
                    continue
                if head_pos and _sentence[head_id - 1]["upostag"] != head_pos:
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
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(
            f"# Search [{head_word},{head_pos}] --{deprel}-> [{dependent_word},{dependent_pos}]\n"
        )
        f.write(f"# {len(search_result)} sentences found\n\n")
        for i, (patterns, sentence) in enumerate(search_result):
            f.write(f"### {i + 1}\n")
            f.writelines("\n".join(patterns) + "\n")
            f.write(sentence.serialize())


if __name__ == "__main__":
    pass

# Created by li huayong on 2020/4/10
import pathlib
import typing
from typing import Any
from typing import Callable
from typing import List

from conllu import parse_incr
from conllu import TokenList

from .type import CONLLUData
from .type import CONLLUDataOrPath


def load(conllu_file_path: str, strict: bool = True) -> CONLLUData:
    """
    加载Conllu数据

    Args:
        conllu_file_path: Conllu文件路径
        strict: 是否是严格的conllu格式

    Returns:
        返回加载的conllu格式数据
    """
    if not pathlib.Path(conllu_file_path).exists():
        raise FileNotFoundError(f"{conllu_file_path}不存在或者无法加载")
    conllu_data = list(parse_incr(open(conllu_file_path)))
    # sdp格式下token的deps不储存信息，但是在conllu格式中储存所有依存信息
    if strict and conllu_data[0][0]["deps"] is None:
        raise RuntimeError("文件完成了加载，但不是标准的conllu格式")
    return conllu_data


def save(conllu_data: List[TokenList], save_conllu_file: str) -> None:
    """
    将Conllu数据保存为.conllu文件形式

    Args:
        conllu_data: 需要保存的conllu格式数据
        save_conllu_file: 保存的文件路径

    Returns:
        无返回值
    """
    with open(save_conllu_file, "w") as f:
        f.writelines([sentence.serialize() + "\n" for sentence in conllu_data])


def is_conllu_data(data: Any, strict: bool = True) -> bool:
    """
    判断是否是合法的conllu格式数据

    Args:
        data:
        strict:

    Returns:
        是否是conllu格式数据
    """
    if isinstance(data, list) and data and isinstance(data[0], TokenList):
        if strict and data[0][0]["deps"] is None:
            return False
        else:
            return True
    else:
        return False


def check_or_load(
    conllu_data_or_file: CONLLUDataOrPath, strict: bool = True
) -> CONLLUData:
    """
    检查是否为合法的conllu数据，若是，则直接返回；如果不是，则判断是否是conllu的文件路径，并尝试加载

    Args:
        conllu_data_or_file: 待判断的数据
        strict: 是否要求严格的conllu格式

    Returns:
        Conllu格式数据
    """
    if is_conllu_data(conllu_data_or_file, strict):
        conllu_data_or_file = typing.cast(CONLLUData, conllu_data_or_file)
        conllu_data = conllu_data_or_file
    elif isinstance(conllu_data_or_file, pathlib.PurePath) or isinstance(
        conllu_data_or_file, str
    ):
        conllu_data = load(str(conllu_data_or_file), strict)
    else:
        raise RuntimeError("输入不是合法的conllu格式或者文件路径")
    return conllu_data


def process(
    input_conllu_data_or_file: CONLLUDataOrPath,
    process_fn: Callable[[TokenList], Any],
    output_conllu_file: str = None,
    strict: bool = True,
):
    """
    自定义处理接口
    接受一个自定义处理函数，接口函数会将每个句子传入自定义处理函数，
    然后接收自定义函数的返回值，如果返回值是None，则不保存；若非None，则保存
    若最后计算得到的数据符合CoNllu的格式，则会写入文件，同时返回；若非CoNllu格式，则只返回

    Args:
        input_conllu_data_or_file: 待处理的conllu数据或者文件路径
        process_fn: 自定义处理函数
        output_conllu_file: 处理的输出conllu文件
        strict: 是否严格要求必须是conllu格式

    Returns:
        返回处理后的结果

    """
    input_conllu_data = check_or_load(input_conllu_data_or_file, strict)
    output_result = []
    for sentence in input_conllu_data:
        output_sentence = process_fn(sentence)
        if output_sentence:
            output_result.append(output_sentence)
    if output_conllu_file and is_conllu_data(output_result):
        save(output_result, output_conllu_file)
    return output_result


if __name__ == "__main__":
    pass

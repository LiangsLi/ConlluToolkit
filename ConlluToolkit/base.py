# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
import json
import pathlib
from pprint import pprint
from typing import List, Tuple, Any
from conllu import parse, parse_incr, TokenList
from .type import CONLLUData, CONLLUDataOrPath


def load(conllu_file_path: str, strict: bool = True)->CONLLUData:
    """
    加载Conllu数据

    Args:
        conllu_file_path: Conllu文件路径
        strict: 是否是严格的conllu格式

    Returns:
        返回加载的conllu格式数据
    """
    if not pathlib.Path(conllu_file_path).exists():
        raise FileNotFoundError(f'{conllu_file_path}不存在或者无法加载')
    conllu_data = list(parse_incr(open(conllu_file_path)))
    # sdp格式下token的deps不储存信息，但是在conllu格式中储存所有依存信息
    if strict and conllu_data[0][0]['deps'] is None:
        raise RuntimeError('文件完成了加载，但不是标准的conllu格式')
    return conllu_data


def save(conllu_data: List[TokenList], save_conllu_file: str)->None:
    """
    将Conllu数据保存为.conllu文件形式

    Args:
        conllu_data: 需要保存的conllu格式数据
        save_conllu_file: 保存的文件路径

    Returns:
        无返回值
    """
    with open(save_conllu_file, 'w') as f:
        f.writelines([sentence.serialize() + "\n" for sentence in conllu_data])


def is_conllu_data(data: Any, strict: bool = True)->bool:
    """
    判断是否是合法的conllu格式数据

    Args:
        data:
        strict:

    Returns:
        是否是conllu格式数据
    """
    if type(data) == list and data and type(data[0]) == TokenList:
        if strict and data[0][0]['deps'] is None:
            return False
        else:
            return True
    else:
        return False


def check_or_load(conllu_data_or_file: CONLLUDataOrPath, strict: bool = True)->CONLLUData:
    """
    检查是否为合法的conllu数据，若是，则直接返回；如果不是，则判断是否是conllu的文件路径，并尝试加载

    Args:
        conllu_data_or_file: 待判断的数据
        strict: 是否要求严格的conllu格式

    Returns:
        Conllu格式数据
    """
    if is_conllu_data(conllu_data_or_file, strict):
        conllu_data = conllu_data_or_file
    elif type(conllu_data_or_file) in [pathlib.PosixPath, str]:
        conllu_data = load(str(conllu_data_or_file), strict)
    else:
        raise RuntimeError('输入不是合法的conllu格式或者文件路径')
    return conllu_data


if __name__ == '__main__':
    pass

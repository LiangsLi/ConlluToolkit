# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
import json
import pathlib
from pprint import pprint
from typing import List, Tuple
from conllu import parse, parse_incr, TokenList


def load(conllu_file_path: str, strict=True):
    if not pathlib.Path(conllu_file_path).exists():
        raise FileNotFoundError(f'{conllu_file_path}不存在或者无法加载')
    conllu_data = list(parse_incr(open(conllu_file_path)))
    # sdp格式下token的deps不储存信息，但是在conllu格式中储存所有依存信息
    if strict and conllu_data[0][0]['deps'] is None:
        raise RuntimeError('文件完成了加载，但不是标准的conllu格式')
    return conllu_data


def save(conllu_data: List[TokenList], save_conllu_file: str):
    with open(save_conllu_file, 'w') as f:
        f.writelines([sentence.serialize() + "\n" for sentence in conllu_data])


def is_conllu_data(data, strict=True):
    if type(data) == list and data and type(data[0]) == TokenList:
        if strict and data[0][0]['deps'] is None:
            return False
        else:
            return True
    else:
        return False


def check_or_load(conllu_data_or_file, strict=True):
    if is_conllu_data(conllu_data_or_file, strict):
        conllu_data = conllu_data_or_file
    elif type(conllu_data_or_file) in [pathlib.PosixPath, str]:
        conllu_data = load(str(conllu_data_or_file), strict)
    else:
        raise RuntimeError('输入不是合法的conllu格式或者文件路径')
    return conllu_data


if __name__ == '__main__':
    pass

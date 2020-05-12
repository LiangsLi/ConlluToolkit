# =========================================
# conlluToolkit-split
# Created by li huayong on 2020/5/12
# =========================================
import pathlib
import random
from typing import Tuple
from typing import Union

from .base import check_or_load
from .base import save
from .type import CONLLUData
from .type import CONLLUDataOrPath


def split_date_set(  # noqa: C901
    conllu_data_or_file: CONLLUDataOrPath,
    train: Union[int, float],
    dev: Union[int, float],
    test: Union[int, float],
    output_dir: Union[pathlib.PurePath, str],
    shuffle: bool = True,
    strict: bool = True,
) -> Tuple[CONLLUData, CONLLUData, CONLLUData]:
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
        raise RuntimeError(f"output_dir({output_dir} is not dir)")
    conllu_data: CONLLUData = check_or_load(conllu_data_or_file, strict)
    sentence_num = len(conllu_data)
    if train == 0 or test == 0:
        raise RuntimeError("train和test数量不能为0")
    if 0 < train < 1:
        if dev > 1 or test > 1:
            raise RuntimeError("如果train为比例，则dev和test都必须为比例")
        if (dev + train + test) != 1:
            raise RuntimeError("比例之和必须为1")
        is_ratio = True
    else:
        # train >=1，此时不再视为比例，而是视为句子数量
        if train % 1 != 0 or dev % 1 != 0 or test % 1 != 0:
            raise RuntimeError("数量只能为整数")
        if (train + dev + test) != sentence_num:
            raise RuntimeError(f"数量之和必须等于总句子数({sentence_num})")
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
    dev_data = conllu_data[train_data_num : train_data_num + dev_data_num]
    test_data = conllu_data[train_data_num + dev_data_num :]
    output_dir = pathlib.Path(output_dir)
    if len(train_data) > 0:
        save(train_data, str(output_dir / f"train.{len(train_data)}.conllu"))
    if len(dev_data) > 0:
        save(dev_data, str(output_dir / f"dev.{len(dev_data)}.conllu"))
    if len(test_data) > 0:
        save(test_data, str(output_dir / f"test.{len(train_data)}.conllu"))
    return train_data, dev_data, test_data

# flake8: noqa
# type: ignore
# Created by li huayong on 2020/4/10
import sys

sys.path.append("..")

from conllutoolkit.statistic import diff


if __name__ == "__main__":
    diff(
        "tmp/text.test.coarse.conllu",
        "tmp/coarse_text.test.conllu",
        "tmp/coarse_text_test_diff.txt",
        ignore_pos=True,
    )

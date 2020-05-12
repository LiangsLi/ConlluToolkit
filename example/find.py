# Created by li huayong on 2020/4/11
import sys

from conllutoolkit.find import find_dependency
from conllutoolkit.find import find_pattern

sys.path.append("..")


def main():
    find_pattern("test.coarse.conllu", "find.pattern.txt", pattern="分化因子")
    find_dependency(
        "test.coarse.conllu", "find.dependency.txt", deprel="FEAT", dependent_pos="v"
    )


if __name__ == "__main__":
    main()

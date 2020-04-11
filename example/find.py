# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/11
import sys

sys.path.append('..')
from conlluprocessor import find_dependency, find_pattern


def main():
    find_pattern('test.coarse.conllu', 'find.pattern.txt', pattern='分化因子')
    find_dependency('test.coarse.conllu', 'find.dependency.txt', deprel='FEAT', dependent_pos='v')


if __name__ == '__main__':
    main()

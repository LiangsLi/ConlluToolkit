# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
from conlluprocessor import diff

if __name__ == '__main__':
    diff(
        'text.test.coarse.conllu',
        'coarse_text.test.conllu',
        'coarse_text_test_diff.txt',ignore_pos=True)

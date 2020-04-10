# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
from conlluprocessor import diff

if __name__ == '__main__':
    diff(
        '/home/liangs/MyCodes/doing_codes/CSDP_Biaffine_Parser_lhy/CSDP_Biaffine_Parser_lhy/dataset/sem16_2019/fine_text.train.cor.sdp.conllu',
        '/home/liangs/MyCodes/doing_codes/CSDP_Biaffine_Parser_lhy/CSDP_Biaffine_Parser_lhy/dataset/SemEval-2016-master/train/text.train.conll.conllu',
        'text_train_diff.txt')

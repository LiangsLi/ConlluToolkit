# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10
import json
import argparse
import sys
sys.path.append('..')
from conlluprocessor import process

with open('coarse2fine.json', 'r', encoding='utf-8')as f:
    coarse2fine_map = json.load(f)
coarse2fine_map['ROOT'] = ['Root']
fine2coarse_map = {}
for coarse, fines in coarse2fine_map.items():
    for fine in fines:
        fine2coarse_map[fine] = coarse


def change_gain(input_file, output_file):
    def change_fun(sentence):
        for token in sentence:
            token['deprel'] = fine2coarse_map[token['deprel']]
            deps = []
            for dep in token['deps']:
                deps.append((fine2coarse_map[dep[0]], dep[1]))
            token['deps'] = deps
        return sentence

    process(input_file, process_fn=change_fun, output_conllu_file=output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='输入细粒度conllu文件', default='fine_text.test.cor.sdp.conllu')
    parser.add_argument('-o', '--output', help='输出粗粒度conllu文件', default='text.test.coarse.conllu')
    args = parser.parse_args()
    change_gain(input_file=args.input, output_file=args.output)


if __name__ == '__main__':
    main()

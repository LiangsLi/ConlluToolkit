# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10


def semeval16_to_conllu(semeval16_filename: str, conllu_filename: str) -> None:
    """
    将semeval16使用的原始数据格式转换为标准的conllu格式
    强烈建议使用标准的conllu格式保存语义/句法依存结果，semeval16使用的原始数据格式对数据处理并不友好
    conlluprocessor的方法基于标准的conllu格式编写，处理semeval格式时会出现错误！

    Args:
        semeval16_filename: semeval16格式的文件
        conllu_filename: 输出的conllu格式文件

    Returns:
        无返回值
    """
    with open(semeval16_filename, encoding='utf-8') as f, open(conllu_filename, 'w', encoding='utf-8') as g:
        sents = f.read().strip().split('\n\n')
        for sent in sents:
            conllu_form = []
            words = []
            lines = sent.strip().split('\n')
            for line in lines:
                if line.startswith('#'):
                    conllu_form.append(line)
                    continue
                items = line.strip().split('\t')
                # print(items)
                if int(items[0]) == len(words) + 1:
                    if items[6] is not '_' and items[7] is not '_':
                        items[8] = items[6] + ':' + items[7]
                    words.append(items)
                elif int(items[0]) == len(words):
                    words[-1][8] += '|' + items[6] + ':' + items[7]
                else:
                    print("Error:{}".format(line))
            for word in words:
                conllu_form.append('\t'.join(word))
            g.write('\n'.join(conllu_form) + '\n\n')


def conllu_to_semeval16(conllu_filename: str, semeval16_filename: str) -> None:
    """
    将conllu格式的数据转化为semeval16使用的原始数据格式
    强烈建议使用标准的conllu格式保存语义/句法依存结果，semeval16使用的原始数据格式对数据处理并不友好
    conlluprocessor的方法基于标准的conllu格式编写，处理semeval格式时会出现错误！

    Args:
        conllu_filename: conllu格式文件
        semeval16_filename: 输出的semeval16格式文件

    Returns:
        无返回值
    """
    with open(conllu_filename, encoding='utf-8') as f, open(semeval16_filename, 'w', encoding='utf-8') as g:
        buff = []
        for line in f:
            line = line.strip('\n')
            items = line.split('\t')
            if len(items) == 10:
                # Add it to the buffer
                buff.append(items)
            elif buff:
                for i, items in enumerate(buff):
                    if items[8] != '_':
                        nodes = items[8].split('|')
                        for node in nodes:
                            words = items
                            # copy xpos to upos
                            words[3] = words[4]
                            node = node.split(':', 1)
                            node[0] = int(node[0])
                            words[6], words[7], words[8] = str(node[0]), node[1], '_'
                            g.write('\t'.join(words) + '\n')
                    else:
                        g.write('\t'.join(items) + '\n')
                g.write('\n')
                buff = []


if __name__ == '__main__':
    pass

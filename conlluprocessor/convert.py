# -*- coding: utf-8 -*-
# Created by li huayong on 2020/4/10


def sdp_to_conllu(sdp_filename, conllu_filename):
    with open(sdp_filename, encoding='utf-8') as f, open(conllu_filename, 'w', encoding='utf-8') as g:
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


def conllu_to_sdp(conllu_filename, sdp_filename):
    with open(conllu_filename, encoding='utf-8') as f, open(sdp_filename, 'w', encoding='utf-8') as g:
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

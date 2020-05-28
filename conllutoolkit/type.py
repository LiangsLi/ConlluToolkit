# Created by li huayong on 2020/4/11
from typing import List
from typing import Union

from conllu import TokenList

CONLLUData = List[TokenList]
CONLLUDataOrPath = Union[str, CONLLUData]

""" About TokenList:

### token:
    1	村	村	NN	NN	_	4	LOC	4:LOC	_

### parser result (item in TokenList):
    OrderedDict([('id', 1),
             ('form', '村'),
             ('lemma', '村'),
             ('upostag', 'NN'),
             ('xpostag', 'NN'),
             ('feats', None),
             ('head', 4),
             ('deprel', 'LOC'),
             ('deps', [('LOC', 4)]),
             ('misc', None)])

"""

if __name__ == "__main__":
    pass

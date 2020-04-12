# conlluprocessor package

## Submodules

## conlluprocessor.base module


### conlluprocessor.base.check_or_load(conllu_data_or_file, strict=True)

### conlluprocessor.base.is_conllu_data(data, strict=True)

### conlluprocessor.base.load(conllu_file_path, strict=True)

### conlluprocessor.base.save(conllu_data, save_conllu_file)
## conlluprocessor.convert module


### conlluprocessor.convert.conllu_to_sdp(conllu_filename, sdp_filename)

### conlluprocessor.convert.sdp_to_conllu(sdp_filename, conllu_filename)
## conlluprocessor.future module


### conlluprocessor.future.generate_raw_conllu(raw_sentences, output_file)

### conlluprocessor.future.word_dependency2char_dependency(conllu_file_or_data, output_file)
## conlluprocessor.statistic module


### conlluprocessor.statistic.statistic_non_projective(sentence_dep_pairs)
统计传入的依存序号列表中是否存在非投射现象，以及非投射的数量
:type sentence_dep_pairs: `List`[`Tuple`[`int`, `int`]]
:param sentence_dep_pairs: List[Tuple[int]]
:return:


### conlluprocessor.statistic.statistics(conllu_data)
统计传入的conllu data（使用conllu模块加载）
conllu模块:[https://github.com/EmilStenstrom/conllu](https://github.com/EmilStenstrom/conllu)
:type conllu_data: `List`[`TokenList`]
:param conllu_data: List[TokenList] conllu数据
:return: tuple：(result:Str, token_vocab:Counter, label_vocab:Counter) 统计结果；词表；依存标签表

## conlluprocessor.type module

## Module contents


### conlluprocessor.diff(conllu_data_or_file_a, conllu_data_or_file_b, output_file, strict=True, ignore_root_id=True, ignore_case=True, ignore_pos=False)
比较两个conllu文件或者数据，并输出不同
不同于原始的diff，这里比较的时候无视句子的顺利，而且以句子为单位比较


* **Parameters**

    
    * **conllu_data_or_file_a** (`Union`[`str`, `List`[`TokenList`]]) – conllu数据或者文件a


    * **conllu_data_or_file_b** (`Union`[`str`, `List`[`TokenList`]]) – conllu数据或者文件b


    * **output_file** (`str`) – 比较结果的输出文件


    * **strict** (`bool`) – 是否要求是严格的conllu文件


    * **ignore_root_id** (`bool`) – 是否无视ROOT的根节点序号差异


    * **ignore_case** (`bool`) – 是否无视依存标签的大小写差异


    * **ignore_pos** (`bool`) – 是否无视词性的差异



* **Return type**

    `None`



* **Returns**

    无返回值



### conlluprocessor.find_dependency(conllu_data_or_file, output_file, head_word=None, head_pos=None, deprel=None, dependent_word=None, dependent_pos=None)
依据依存条件在conllu数据或者文件中查找句子
这里支持的依存条件为：头节点单词、头节点词性、尾节点单词、尾节点词性、依存标签，以上条件可为空，但是至少有一个不为空


* **Parameters**

    
    * **conllu_data_or_file** (`Union`[`str`, `List`[`TokenList`]]) – 查询的conllu数据或者文件


    * **output_file** (`str`) – 查询结果输出文件


    * **head_word** (`Optional`[`str`]) – 头节点单词


    * **head_pos** (`Optional`[`str`]) – 头节点词性


    * **deprel** (`Optional`[`str`]) – 依存标签


    * **dependent_word** (`Optional`[`str`]) – 尾节点单词


    * **dependent_pos** (`Optional`[`str`]) – 尾节点词性



* **Return type**

    `None`



* **Returns**

    无返回值



### conlluprocessor.find_pattern(conllu_data_or_file, output_file, pattern)
依据正则在conllu数据或者文件中查询句子
只匹配句子形式


* **Parameters**

    
    * **conllu_data_or_file** (`Union`[`str`, `List`[`TokenList`]]) – 查询的conllu数据或者文件


    * **output_file** (`str`) – 查询结果输出文件


    * **pattern** (`str`) – 合法的正则模式



* **Return type**

    `None`



* **Returns**

    无返回值



### conlluprocessor.process(input_conllu_data_or_file, process_fn, output_conllu_file=None, strict=True)

### conlluprocessor.split_date_set(conllu_data_or_file, train, dev, test, output_dir, shuffle=True, strict=True)
按照比例或者数量切分数据集，结果写入文件同时返回


* **Parameters**

    
    * **conllu_data_or_file** (`Union`[`str`, `List`[`TokenList`]]) – 等待切分的conllu数据或者文件路径


    * **train** (`Union`[`int`, `float`]) – 训练集大小（数量或者比例）


    * **dev** (`Union`[`int`, `float`, `None`]) – 验证集大小（数量或者比例）


    * **test** (`Union`[`int`, `float`]) – 测试集大小（数量或者比例）


    * **output_dir** (`str`) – 输出文件的文件夹路径


    * **shuffle** (`bool`) – 切分前是否打乱顺利


    * **strict** (`bool`) – 是否要求输入数据是必须是conllu（如False则支持semeval16的原始数据格式）



* **Return type**

    `Tuple`



* **Returns**

    返回切分后的训练集、验证集、测试集数据

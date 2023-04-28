import json
from copy import deepcopy

def rclass(evidence_list: list):
    """
    根据evidence列表判断属于哪个类别

    输入
    ------
     evidence_list: 证据列表

    输出
    ------
     category: 实体关系对所属的证据类别
    """
    assert 0 <= len(evidence_list) <= 9
    return len(evidence_list)


def word_mapping(words):
    """
    统计vertexSet中各个词所属的句子列表

    输入
    ------
     words: vertexSet结构

    输出
    ------
     word_map: 映射表，包含各个词所属的句子列表
    """
    word_map = {}

    for i, items in enumerate(words):
        word_map[i] = []

        for item in items:
            word_map[i].append(item['sent_id'])

    return word_map


def stat_module(words, labels):
    """
    统计一篇文档中mixture和multiple的数量

    输入
    ------
     words: vertexSet结构
     labels: labels结构

    输出
    ------
     mixture: 统计各个类别的mixture数量
     multiple: 统计各个类别的multiple数量
    """
    mixture = [0 for _ in range(10)]
    multiple = [0 for _ in range(10)]

    word_map = word_mapping(words)

    for label in labels:
        h_sents = word_map[label['h']]
        t_sents = word_map[label['t']]
        e_class = rclass(label['evidence'])
        cooccur = [val for val in h_sents if val in t_sents]

        # if len(cooccur) > 0:
        if any(t in label['evidence'] for t in cooccur):
            mixture[e_class] += 1
            if 'type' not in label:
                if e_class<2:
                    label['type']='single'
                else:
                    label['type'] = 'mixture'
        else:
            multiple[e_class] += 1
            if 'type' not in label:
                if e_class < 2:
                    label['type'] = 'single'
                else:
                    label['type'] = 'multiple'

    return mixture, multiple


def relation_statis(data):
    """
    统计所有文档中mixture和multiple的数量

    输入
    ------
     DocREDdata: 数据集

    输出
    ------
     mixture_list: 统计各个类别的mixture数量
     multiple_list: 统计各个类别的multiple数量
    """
    data=deepcopy(data)
    single_list=[0 for _ in range(2)]
    mixture_list = [0 for _ in range(10)]
    multiple_list = [0 for _ in range(10)]

    for slice in data:
        mixture, multiple = stat_module(slice['vertexSet'], slice['labels'])

        for i in range(2):
            single_list[i]+=mixture[i]+multiple[i]

        for i in range(2, 10):
            mixture_list[i] += mixture[i]
            multiple_list[i] += multiple[i]

    return single_list,mixture_list, multiple_list,data


def main(data_file):
    f = open(data_file, 'r', encoding='utf-8')
    data = json.load(f)
    single_list, mixture_list, multiple_list,data= relation_statis(data)

    print('single ', single_list)
    print('mixture ', mixture_list)
    print('multiple', multiple_list)
    print('mixture (2-3) ', mixture_list[2] + mixture_list[3])
    print('mixture (4-5) ', mixture_list[4] + mixture_list[5])
    print('mixture (6-7) ', mixture_list[6] + mixture_list[7])
    print('mixture (8-9) ', mixture_list[8] + mixture_list[9])
    print('multiple (2-3)', multiple_list[2] + multiple_list[3])
    print('multiple (4-5)', multiple_list[4] + multiple_list[5])
    print('multiple (6-7)', multiple_list[6] + multiple_list[7])
    print('multiple (8-9)', multiple_list[8] + multiple_list[9])

    print('one evidence', single_list)
    print('multiple with cooccurance', sum(mixture_list[2:]))
    print('multiple without cooccurance', sum(multiple_list[2:]))


if __name__ == '__main__':
    main('./DocREDdata/dev.json')

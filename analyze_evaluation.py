import os
import json
import numpy as np
from MixMultiple import relation_statis


def dict_sum(x, ctype, dtype, rang=None):
    res = 0
    if rang:
        for i in rang:
            res += x[ctype][i][dtype]
    else:
        for i in range(len(x[ctype])):
            res += x[ctype][i][dtype]
    return res


def gen_train_facts(data_file_name, truth_dir):
    fact_file_name = data_file_name[data_file_name.find("train_"):]
    fact_file_name = os.path.join(
        truth_dir, fact_file_name.replace(".json", ".fact"))

    if os.path.exists(fact_file_name):
        fact_in_train = set([])
        triples = json.load(open(fact_file_name))
        for x in triples:
            fact_in_train.add(tuple(x))
        return fact_in_train

    fact_in_train = set([])
    ori_data = json.load(open(data_file_name))
    for data in ori_data:
        vertexSet = data['vertexSet']
        for label in data['labels']:
            rel = label['r']
            for n1 in vertexSet[label['h']]:
                for n2 in vertexSet[label['t']]:
                    fact_in_train.add((n1['name'], n2['name'], rel))

    json.dump(list(fact_in_train), open(fact_file_name, "w"))

    return fact_in_train


def official_evaluate(tmp, path):
    '''
        Adapted from the official evaluation code
    '''
    truth_dir = os.path.join(path, 'ref')

    if not os.path.exists(truth_dir):
        os.makedirs(truth_dir)

    fact_in_train_annotated = gen_train_facts(
        os.path.join(path, "train_annotated.json"), truth_dir)
    fact_in_train_distant = gen_train_facts(
        os.path.join(path, "train_distant.json"), truth_dir)

    # [wyf@2021-06-01]
    truth = json.load(open(os.path.join(path, "ref/dev.json")))
    single_list, mixture_list, multiple_list, truth = relation_statis(truth)
    # print('dev.json loaded.')

    # set of truth ('title', 'relation', head_index, tail_index): {'evidence': set of evidence_index, 'type': 'mixture'}
    std = {}
    tot_evidences = 0  # total truth evidence count, used for evidence recall metric
    titleset = set([])  # truth title set, used for unambiguity

    title2vectexSet = {}  # find truth vectexes by title

    for x in truth:
        title = x['title']
        titleset.add(title)

        vertexSet = x['vertexSet']
        title2vectexSet[title] = vertexSet

        for label in x['labels']:
            r = label['r']
            h_idx = label['h']
            t_idx = label['t']
            std[(title, r, h_idx, t_idx)] = {'evidence': set(
                label['evidence']), 'type': label['type']}
            tot_evidences += len(label['evidence'])

    # print('truth answer loaded.')

    tot_relations = len(std)  # specifically it means total triples count
    tmp.sort(key=lambda x: (x['title'], x['h_idx'], x['t_idx'], x['r']))
    # predict answers, {'title': '(I Am) The Seeker', 'h_idx': 0, 't_idx': 1, 'r': 'P175'}
    submission_answer = [tmp[0]]
    for i in range(1, len(tmp)):  # remove redundance
        x = tmp[i]
        y = tmp[i - 1]
        if (x['title'], x['h_idx'], x['t_idx'], x['r']) != (y['title'], y['h_idx'], y['t_idx'], y['r']):
            submission_answer.append(tmp[i])

    # print('predict answer loaded.')

    correct_re = 0
    correct_evidence = 0
    pred_evi = 0

    correct_in_train_annotated = 0
    correct_in_train_distant = 0
    # titleset2 = set([])

    # count metric by category [wyf@2021-06-01]
    correct_by_category = {
        'single': [0 for _ in range(2)],
        'mixture': [0 for _ in range(10)],
        'multiple': [0 for _ in range(10)]
    }
    correct_in_train_ann_by_category = {
        'single': [0 for _ in range(2)],
        'mixture': [0 for _ in range(10)],
        'multiple': [0 for _ in range(10)]
    }
    correct_in_train_dis_by_category = {
        'single': [0 for _ in range(2)],
        'mixture': [0 for _ in range(10)],
        'multiple': [0 for _ in range(10)]
    }

    for x in submission_answer:
        title = x['title']
        h_idx = x['h_idx']
        t_idx = x['t_idx']
        r = x['r']
        # titleset2.add(title)
        if title not in title2vectexSet:
            continue
        vertexSet = title2vectexSet[title]

        if 'evidence' in x:
            evi = set(x['evidence'])
        else:
            evi = set([])
        pred_evi += len(evi)

        if (title, r, h_idx, t_idx) in std:  # if predict is right, check evidence
            correct_re += 1
            stdevi = std[(title, r, h_idx, t_idx)]['evidence']
            correct_evidence += len(stdevi & evi)

            # count recall by category [wyf@2021-06-01]
            category = len(stdevi)
            ctype = std[(title, r, h_idx, t_idx)]['type']
            correct_by_category[ctype][category] += 1

            # check if in train_annotated or train_distant
            in_train_annotated = in_train_distant = False
            for n1 in vertexSet[h_idx]:
                for n2 in vertexSet[t_idx]:
                    if (n1['name'], n2['name'], r) in fact_in_train_annotated:
                        in_train_annotated = True
                    if (n1['name'], n2['name'], r) in fact_in_train_distant:
                        in_train_distant = True
            if in_train_annotated:
                correct_in_train_annotated += 1
                # count overlappings by category [wyf@2021-06-01]
                correct_in_train_ann_by_category[ctype][category] += 1
            if in_train_distant:
                correct_in_train_distant += 1
                # count overlappings by category [wyf@2021-06-01]
                correct_in_train_dis_by_category[ctype][category] += 1

    re_p = 1.0 * correct_re / len(submission_answer)
    re_r = 1.0 * correct_re / tot_relations
    if re_p + re_r == 0:
        re_f1 = 0
    else:
        re_f1 = 2.0 * re_p * re_r / (re_p + re_r)

    evi_p = 1.0 * correct_evidence / pred_evi if pred_evi > 0 else 0
    evi_r = 1.0 * correct_evidence / tot_evidences
    if evi_p + evi_r == 0:
        evi_f1 = 0
    else:
        evi_f1 = 2.0 * evi_p * evi_r / (evi_p + evi_r)

    re_p_ignore_train_annotated = 1.0 * (correct_re - correct_in_train_annotated) / (
        len(submission_answer) - correct_in_train_annotated + 1e-5)
    re_p_ignore_train = 1.0 * (correct_re - correct_in_train_distant) / \
        (len(submission_answer) - correct_in_train_distant + 1e-5)

    if re_p_ignore_train_annotated + re_r == 0:
        re_f1_ignore_train_annotated = 0
    else:
        re_f1_ignore_train_annotated = 2.0 * re_p_ignore_train_annotated * \
            re_r / (re_p_ignore_train_annotated + re_r)

    if re_p_ignore_train + re_r == 0:
        re_f1_ignore_train = 0
    else:
        re_f1_ignore_train = 2.0 * re_p_ignore_train * \
            re_r / (re_p_ignore_train + re_r)

    # calculate metric by category [wyf@2021-06-01]
    re_by_category = {
        'single': [{'molec': 0, 'denom': 0} for _ in range(2)],
        'mixture': [{'molec': 0, 'denom': 0} for _ in range(10)],
        'multiple': [{'molec': 0, 'denom': 0} for _ in range(10)]
    }

    for i in range(2):
        if single_list[i] > 0.0:
            re_by_category['single'][i]['molec'] = correct_by_category['single'][i]
            re_by_category['single'][i]['denom'] = single_list[i]

    for i in range(2, 10):
        if mixture_list[i] > 0.0:
            re_by_category['mixture'][i]['molec'] = correct_by_category['mixture'][i]
            re_by_category['mixture'][i]['denom'] = mixture_list[i]
        if multiple_list[i] > 0.0:
            re_by_category['multiple'][i]['molec'] = correct_by_category['multiple'][i]
            re_by_category['multiple'][i]['denom'] = multiple_list[i]

    return re_f1, evi_f1, re_f1_ignore_train_annotated, re_f1_ignore_train, re_by_category


def main():
    # main result(table 2)
    preds = json.load(open('/home/htt/Desktop/gnn/result_dev_SSAN.json', 'r'))
    re_f1, evi_f1, re_f1_ignore_train_annotated, re_f1_ignore_train, re_by_category = official_evaluate(
        preds, '/home/htt/Desktop/gnn/baseline/code/input_dir/')
    print('re_f1: {:.2%}'.format(re_f1))
    print('evi_f1: {:.2%}'.format(evi_f1))
    print('re_f1_ignore_train_annotated: {:.2%}'.format(
        re_f1_ignore_train_annotated))
    print('re_f1_ignore_train: {:.2%}'.format(re_f1_ignore_train))
    # print category (table 6)
    single = 1.0 * dict_sum(re_by_category, 'single', 'molec', range(1, 2)) / \
        dict_sum(re_by_category, 'single', 'denom', range(1, 2))
    mixture = 1.0 * dict_sum(re_by_category, 'mixture', 'molec') / \
        dict_sum(re_by_category, 'mixture', 'denom')
    multiple = 1.0 * dict_sum(re_by_category, 'multiple', 'molec') / \
        dict_sum(re_by_category, 'multiple', 'denom')
    print('single recall: {:.2%}'.format(single))
    print('mixture recall: {:.2%}'.format(mixture))
    print('multiple recall: {:.2%}'.format(multiple))
    #type and number category(table 6)
    # mixture_2_3 = 1.0 * dict_sum(re_by_category, 'mixture', 'molec', range(
    #     2, 4)) / dict_sum(re_by_category, 'mixture', 'denom', range(2, 4))
    # mixture_4_5 = 1.0 * dict_sum(re_by_category, 'mixture', 'molec', range(
    #     4, 6)) / dict_sum(re_by_category, 'mixture', 'denom', range(4, 6))
    # mixture_6_7 = 1.0 * dict_sum(re_by_category, 'mixture', 'molec', range(
    #     6, 8)) / dict_sum(re_by_category, 'mixture', 'denom', range(6, 8))
    # mixture_8_9 = 1.0 * dict_sum(re_by_category, 'mixture', 'molec', range(
    #     8, 10)) / dict_sum(re_by_category, 'mixture', 'denom', range(8, 10))
    # multiple_2_3 = 1.0 * dict_sum(re_by_category, 'multiple', 'molec', range(
    #     2, 4)) / dict_sum(re_by_category, 'multiple', 'denom', range(2, 4))
    # multiple_4_5 = 1.0 * dict_sum(re_by_category, 'multiple', 'molec', range(
    #     4, 6)) / dict_sum(re_by_category, 'multiple', 'denom', range(4, 6))
    # multiple_6_7 = 1.0 * dict_sum(re_by_category, 'multiple', 'molec', range(
    #     6, 8)) / dict_sum(re_by_category, 'multiple', 'denom', range(6, 8))
    # multiple_8_9 = 1.0 * dict_sum(re_by_category, 'multiple', 'molec', range(
    #     8, 10)) / dict_sum(re_by_category, 'multiple', 'denom', range(8, 10))
    # print('mixture (2, 3) recall: {:.2%}'.format(mixture_2_3))
    # print('mixture (4, 5) recall: {:.2%}'.format(mixture_4_5))
    # print('mixture (6, 7) recall: {:.2%}'.format(mixture_6_7))
    # print('mixture (8, 9) recall: {:.2%}'.format(mixture_8_9))
    # print('multiple (2, 3) recall: {:.2%}'.format(multiple_2_3))
    # print('multiple (4, 5) recall: {:.2%}'.format(multiple_4_5))
    # print('multiple (6, 7) recall: {:.2%}'.format(multiple_6_7))
    # print('multiple (8, 9) recall: {:.2%}'.format(multiple_8_9))
    # evidence number category(fig 7)
    n_0_1 = 1.0 * dict_sum(re_by_category, 'single', 'molec', range(
        0, 2)) / dict_sum(re_by_category, 'single', 'denom', range(0, 2))
    n_2_3 = 1.0 * (dict_sum(re_by_category, 'mixture', 'molec', range(2, 4))
                   + dict_sum(re_by_category, 'multiple', 'molec', range(
                       2, 4))) / (dict_sum(re_by_category, 'mixture', 'denom', range(2, 4))
                                  + dict_sum(re_by_category, 'multiple', 'denom', range(2, 4)))
    n_4_5 = 1.0 * (dict_sum(re_by_category, 'mixture', 'molec', range(4, 6))
                   + dict_sum(re_by_category, 'multiple', 'molec', range(
                       4, 6))) / (dict_sum(re_by_category, 'mixture', 'denom', range(4, 6))
                                  + dict_sum(re_by_category, 'multiple', 'denom', range(4, 6)))
    n_6_7 = 1.0 * (dict_sum(re_by_category, 'mixture', 'molec', range(6, 8))
                   + dict_sum(re_by_category, 'multiple', 'molec', range(
                       6, 8))) / (dict_sum(re_by_category, 'mixture', 'denom', range(6, 8))
                                  + dict_sum(re_by_category, 'multiple', 'denom', range(6, 8)))
    n_8_9 = 1.0 * (dict_sum(re_by_category, 'mixture', 'molec', range(8, 10))
                   + dict_sum(re_by_category, 'multiple', 'molec', range(
                       8, 10))) / (dict_sum(re_by_category, 'mixture', 'denom', range(8, 10))
                                   + dict_sum(re_by_category, 'multiple', 'denom', range(8, 10)))
    print('total (0, 1) recall: {:.2%}'.format(n_0_1))
    print('total (2, 3) recall: {:.2%}'.format(n_2_3))
    print('total (4, 5) recall: {:.2%}'.format(n_4_5))
    print('total (6, 7) recall: {:.2%}'.format(n_6_7))
    print('total (8, 9) recall: {:.2%}'.format(n_8_9))


if __name__ == '__main__':
    main()

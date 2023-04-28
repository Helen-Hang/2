import json
from nltk import data
import pandas as pd
from pathlib import Path
import nltk
nltk.download('punkt')


def pending():
    if (not hasattr(pending, 'x')):
        pending.x = '-'
    print('\r{}'.format(pending.x), end='', flush=True)
    chars = ['-', '\\', '|', '/']
    pending.x = chars[(chars.index(pending.x) + 1) % 4]


def _read_gda_anns(path, dataset):
    print('Read Annotations')
    indicator = 0

    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break

            line = line.split('\n')[0]
            if len(line.split('\t')) == 6:  # vertex
                line = line.split('\t')

                title = str(line[0])
                if title not in dataset:
                    dataset[title] = {}

                if 'title' not in dataset[title]:
                    dataset[title]["title"] = title

                if 'vertexSet' not in dataset[title]:
                    dataset[title]['vertexSet'] = []

                vertex = {}
                vertex['name'] = str(line[3])
                vertex['pos'] = [int(line[1]), int(line[2])]
                vertex['type'] = str(line[4])
                vertex['MESH'] = str(line[5])

                target_group = None
                for group in dataset[title]['vertexSet']:
                    if vertex['MESH'] == group[0]['MESH']:
                        target_group = group
                        break
                if not target_group:
                    dataset[title]['vertexSet'].append([vertex])
                else:
                    target_group.append(vertex)

            if indicator % 10 == 0:
                pending()

            indicator += 1
            if indicator % 100 == 0:
                print(' >>> {}'.format(indicator), end='')

    print()


def _read_gda_sentences(path, dataset):
    print('Read Sentences')
    indicator = 0

    with open(path, 'r') as f:
        while True:
            line = f.readline()
            indicator += 1
            if not line:
                break

            document = []
            while line == '\n':
                line = f.readline()
                indicator += 1
            while line != '\n':
                document.append(line.split('\n')[0])
                line = f.readline()
                indicator += 1

            title = str(document[0])
            if title not in dataset:
                dataset[title] = {}

            if 'title' not in dataset[title]:
                dataset[title]["title"] = title

            dataset[title]['sents'] = []
            for sentence in document[1:]:
                dataset[title]['sents'].append(
                    nltk.word_tokenize(sentence))

            if indicator % 10 == 0:
                pending()

            if indicator % 100 == 0:
                print(' >>> {}'.format(indicator), end='')

    print()


def _read_gda_labels(path, dataset):
    print('Read Labels')
    indicator = 0

    with open(path, 'r') as f:
        df = pd.read_csv(f)

        for i in range(len(df)):
            title = str(df.iloc[i, 0])
            if title not in dataset:
                dataset[title] = {}

            if 'labels' not in dataset[title]:
                dataset[title]['labels'] = []

            label = {}
            label['r'] = str(df.iloc[i, 3])
            label['h'] = str(df.iloc[i, 1])
            label['t'] = str(df.iloc[i, 2])

            dataset[title]['labels'].append(label)

            if indicator % 10 == 0:
                pending()

            indicator += 1
            if indicator % 100 == 0:
                print(' >>> {}'.format(indicator), end='')

    print()


def read_gda(folder, ratio=1.0):
    dataset = {}
    path_anns = Path(folder).joinpath('anns.txt')
    path_sentences = Path(folder).joinpath('sentences.txt')
    path_labels = Path(folder).joinpath('labels.csv')

    _read_gda_anns(path_anns, dataset)
    _read_gda_sentences(path_sentences, dataset)
    _read_gda_labels(path_labels, dataset)

    dataset = list(dataset.values())
    n_documents = len(dataset)
    return dataset[:int(ratio * n_documents)], dataset[int(ratio * n_documents):]


if __name__ == '__main__':
    train_data, dev_data = read_gda(folder='GDA/training_data', ratio=0.8)
    test_data, _ = read_gda(folder='GDA/testing_data')

    json.dump(train_data, open('GDA/train.json', 'w'))
    json.dump(dev_data, open('GDA/dev.json', 'w'))
    json.dump(test_data, open('GDA/test.json', 'w'))

    print("Number of training documents:", len(train_data))
    print("Number of developing documents:", len(dev_data))
    print("Number of testing documents:", len(test_data))

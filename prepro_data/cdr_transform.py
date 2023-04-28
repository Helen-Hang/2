import json
import nltk
nltk.download('punkt')


def pending():
    if (not hasattr(pending, 'x')):
        pending.x = '-'
    print('\r{}'.format(pending.x), end='', flush=True)
    chars = ['-', '\\', '|', '/']
    pending.x = chars[(chars.index(pending.x) + 1) % 4]


def read_cdr(path):
    indicator = 0
    dataset = {}

    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break

            line = line.split('\n')[0]
            if '|t|' in line:  # title
                line = line.split('|t|')

                title = str(line[0])
                if title not in dataset:
                    dataset[title] = {}

                dataset[title]["title"] = title

            elif '|a|' in line:  # sentence
                line = line.split('|a|')

                title = str(line[0])
                if title not in dataset:
                    dataset[title] = {}

                dataset[title]['sents'] = []
                sentences = nltk.sent_tokenize(line[1])
                for sentence in sentences:
                    dataset[title]['sents'].append(
                        nltk.word_tokenize(sentence))

            elif len(line.split()) == 4:  # labels
                line = line.split()

                title = str(line[0])
                if title not in dataset:
                    dataset[title] = {}

                if 'labels' not in dataset[title]:
                    dataset[title]['labels'] = []

                label = {}
                label['r'] = str(line[1])
                label['h'] = str(line[2])
                label['t'] = str(line[3])

                dataset[title]['labels'].append(label)

            elif len(line.split()) > 0:  # vertex
                line = line.split()

                title = str(line[0])
                if title not in dataset:
                    dataset[title] = {}

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

            pending()

            indicator += 1
            if indicator % 100 == 0:
                print(' >>> {}'.format(indicator), end='')

    print()
    return list(dataset.values())


if __name__ == '__main__':
    train_data = read_cdr('CDR/CDR_TrainingSet.PubTator.txt')
    dev_data = read_cdr('CDR/CDR_DevelopmentSet.PubTator.txt')
    test_data = read_cdr('CDR/CDR_TestSet.PubTator.txt')

    json.dump(train_data, open('CDR/train.json', 'w'))
    json.dump(dev_data, open('CDR/dev.json', 'w'))
    json.dump(test_data, open('CDR/test.json', 'w'))

    print("Number of training documents:", len(train_data))
    print("Number of developing documents:", len(dev_data))
    print("Number of testing documents:", len(test_data))

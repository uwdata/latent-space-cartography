# -*- coding: utf-8 -*-

import os
import h5py
import csv
import numpy as np

base = '/Users/yliu0/data/word'

# limit the total amount of words
LIMIT = 10000

# read in word2vec embeddings
def read_w2v_pretrained ():
    from gensim.models import KeyedVectors
    w2v = os.path.join(base, 'GoogleNews-vectors-negative300.bin')
    model = KeyedVectors.load_word2vec_format(w2v, binary=True)
    print(model.most_similar(positive=['woman', 'king'], negative=['man']))

# wrangle word2vec word embeddings trained by us
def read_w2v ():
    folder = '/home/yliu0/data/word2vec'
    dim = 300
    p_in = os.path.join(folder, 'dim{}.txt'.format(dim))
    p_out = os.path.join(folder, 'latent')
    p_h5 = os.path.join(p_out, 'latent{}.h5'.format(dim))
    p_meta = os.path.join(p_out, 'meta{}.csv'.format(dim))

    # create folder
    if not os.path.exists(p_out):
        os.makedirs(p_out)

    meta = []
    res = []
    print('Processing: dim {}'.format(dim))

    # read word embedding input
    with open(p_in, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quoting=csv.QUOTE_NONE)
        i = 0
        for row in reader:
            if len(row) < dim: # skip header rows
                continue
            meta.append([i, row[0]])
            i += 1
            res.append(row[1:])

            # only read the first N rows
            if i >= LIMIT:
                break
    res = np.asarray(res, dtype=float)
    print(res.shape)

    # save meta
    with open(p_meta, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['i', 'name'])
        for m in meta:
            writer.writerow(m)

    # save embedding to hdf5
    f = h5py.File(p_h5, 'w')
    dset = f.create_dataset('latent', data=res)
    f.close()

# wrangle GloVe pre-trained embeddings
def read_glove ():
    cops = ['6B']
    dims = [50, 100, 200, 300]
    for cop in cops:
        for dim in dims:
            # file paths
            folder = os.path.join(base, 'raw', 'glove.{}'.format(cop))
            p_in = os.path.join(folder, 'glove.{}.{}d.txt'.format(cop, dim))
            p_out = os.path.join(base, 'glove{}'.format(cop))
            p_h5 = os.path.join(p_out, 'latent{}.h5'.format(dim))
            p_meta = os.path.join(p_out, 'meta{}.csv'.format(dim))

            # create folder
            if not os.path.exists(p_out):
                os.makedirs(p_out)

            meta = []
            res = []
            print('Processing: {}, {}'.format(cop, dim))

            # read GloVe output
            with open(p_in, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quoting=csv.QUOTE_NONE)
                i = 0
                for row in reader:
                    meta.append([i, row[0]])
                    i += 1
                    res.append(row[1:])

                    # only read the first N rows
                    if i >= LIMIT:
                        break
            res = np.asarray(res, dtype=float)
            print(res.shape)

            # save meta
            with open(p_meta, 'wb') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['i', 'name'])
                for m in meta:
                    writer.writerow(m)

            # save embedding to hdf5
            f = h5py.File(p_h5, 'w')
            dset = f.create_dataset('latent', data=res)
            f.close()

def wrangle_test_result ():
    dims = [50, 100, 200, 300]
    results = [
"""2018-09-04 21:28:37,817: INFO: capital-common-countries: 81.0% (374/462)
2018-09-04 21:28:38,382: INFO: capital-world: 79.0% (564/714)
2018-09-04 21:28:38,454: INFO: currency: 24.4% (21/86)
2018-09-04 21:28:38,939: INFO: city-in-state: 16.3% (100/615)
2018-09-04 21:28:39,106: INFO: family: 82.4% (173/210)
2018-09-04 21:28:39,401: INFO: gram1-adjective-to-adverb: 17.6% (67/380)
2018-09-04 21:28:39,448: INFO: gram2-opposite: 16.1% (9/56)
2018-09-04 21:28:39,876: INFO: gram3-comparative: 56.2% (310/552)
2018-09-04 21:28:40,001: INFO: gram4-superlative: 47.4% (74/156)
2018-09-04 21:28:40,463: INFO: gram5-present-participle: 52.8% (317/600)
2018-09-04 21:28:41,351: INFO: gram6-nationality-adjective: 96.7% (1123/1161)
2018-09-04 21:28:42,111: INFO: gram7-past-tense: 41.7% (414/992)
2018-09-04 21:28:42,507: INFO: gram8-plural: 64.2% (325/506)
2018-09-04 21:28:42,724: INFO: gram9-plural-verbs: 32.0% (87/272)
2018-09-04 21:28:42,725: INFO: total: 58.5% (3958/6762)""",
"""2018-09-04 21:29:18,322: INFO: capital-common-countries: 94.2% (435/462)
2018-09-04 21:29:19,050: INFO: capital-world: 92.4% (660/714)
2018-09-04 21:29:19,140: INFO: currency: 29.1% (25/86)
2018-09-04 21:29:19,728: INFO: city-in-state: 31.2% (192/615)
2018-09-04 21:29:19,922: INFO: family: 91.0% (191/210)
2018-09-04 21:29:20,334: INFO: gram1-adjective-to-adverb: 30.0% (114/380)
2018-09-04 21:29:20,389: INFO: gram2-opposite: 16.1% (9/56)
2018-09-04 21:29:20,892: INFO: gram3-comparative: 81.0% (447/552)
2018-09-04 21:29:21,051: INFO: gram4-superlative: 73.1% (114/156)
2018-09-04 21:29:21,607: INFO: gram5-present-participle: 78.0% (468/600)
2018-09-04 21:29:22,681: INFO: gram6-nationality-adjective: 97.5% (1132/1161)
2018-09-04 21:29:23,655: INFO: gram7-past-tense: 60.2% (597/992)
2018-09-04 21:29:24,108: INFO: gram8-plural: 74.9% (379/506)
2018-09-04 21:29:24,363: INFO: gram9-plural-verbs: 55.5% (151/272)
2018-09-04 21:29:24,363: INFO: total: 72.7% (4914/6762)""",
"""2018-09-04 21:30:35,197: INFO: capital-common-countries: 95.2% (440/462)
2018-09-04 21:30:35,998: INFO: capital-world: 95.1% (679/714)
2018-09-04 21:30:36,087: INFO: currency: 27.9% (24/86)
2018-09-04 21:30:36,755: INFO: city-in-state: 58.7% (361/615)
2018-09-04 21:30:36,990: INFO: family: 92.9% (195/210)
2018-09-04 21:30:37,403: INFO: gram1-adjective-to-adverb: 27.6% (105/380)
2018-09-04 21:30:37,459: INFO: gram2-opposite: 23.2% (13/56)
2018-09-04 21:30:37,987: INFO: gram3-comparative: 84.8% (468/552)
2018-09-04 21:30:38,137: INFO: gram4-superlative: 83.3% (130/156)
2018-09-04 21:30:38,727: INFO: gram5-present-participle: 76.8% (461/600)
2018-09-04 21:30:39,818: INFO: gram6-nationality-adjective: 100.0% (1161/1161)
2018-09-04 21:30:40,736: INFO: gram7-past-tense: 62.9% (624/992)
2018-09-04 21:30:41,209: INFO: gram8-plural: 77.9% (394/506)
2018-09-04 21:30:41,467: INFO: gram9-plural-verbs: 57.4% (156/272)
2018-09-04 21:30:41,467: INFO: total: 77.1% (5211/6762)""",
"""2018-09-04 21:32:20,589: INFO: capital-common-countries: 95.7% (442/462)
2018-09-04 21:32:21,485: INFO: capital-world: 95.7% (683/714)
2018-09-04 21:32:21,597: INFO: currency: 27.9% (24/86)
2018-09-04 21:32:22,344: INFO: city-in-state: 72.8% (448/615)
2018-09-04 21:32:22,597: INFO: family: 94.3% (198/210)
2018-09-04 21:32:23,045: INFO: gram1-adjective-to-adverb: 25.5% (97/380)
2018-09-04 21:32:23,116: INFO: gram2-opposite: 23.2% (13/56)
2018-09-04 21:32:23,753: INFO: gram3-comparative: 85.9% (474/552)
2018-09-04 21:32:23,936: INFO: gram4-superlative: 84.6% (132/156)
2018-09-04 21:32:24,626: INFO: gram5-present-participle: 78.7% (472/600)
2018-09-04 21:32:25,943: INFO: gram6-nationality-adjective: 100.0% (1161/1161)
2018-09-04 21:32:27,075: INFO: gram7-past-tense: 63.9% (634/992)
2018-09-04 21:32:27,653: INFO: gram8-plural: 81.2% (411/506)
2018-09-04 21:32:27,970: INFO: gram9-plural-verbs: 58.5% (159/272)
2018-09-04 21:32:27,977: INFO: total: 79.1% (5348/6762)"""
    ]

    res = []
    for i in range(len(dims)):
        dim = dims[i]
        s = results[i]
        for line in s.split('\n'):
            token = line.split(':')
            name = token[-2].strip()
            tt = token[-1].split('%')
            score = float(tt[0].strip())
            res.append(['analogy', dim, name, score])

    out = '../../client/data/glove_6b/initial.csv'
    with open(out, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['type', 'dim', 'subtype', 'score'])
        for row in res:
            writer.writerow(row)

if __name__ == '__main__':
    # read_glove()
    # read_w2v()
    wrangle_test_result()

# -*- coding: utf-8 -*-

import os
import h5py
import csv
import numpy as np

base = '/Users/yliu0/data/word'

# limit the total amount of words
LIMIT = 10000

# read in word2vec embeddings
def read_w2v ():
    from gensim.models import KeyedVectors
    w2v = os.path.join(base, 'GoogleNews-vectors-negative300.bin')
    model = KeyedVectors.load_word2vec_format(w2v, binary=True)
    print(model.most_similar(positive=['woman', 'king'], negative=['man']))

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

if __name__ == '__main__':
    read_glove()

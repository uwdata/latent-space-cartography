# -*- coding: utf-8 -*-
# pairwise cosine similarity of random pairs in the latent space

import os
import h5py
import sys
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ugly way to import a file from another directory ...
sys.path.append(os.path.join(os.path.dirname(__file__), '../model'))
import model

from config_glove_6b import dset

# for absolute path
def abs_path (rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)

# read latent space
def read_ls (latent_dim):
    rawpath = abs_path('../client/data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])
    return X

def cosine (latent_dim):
    X = read_ls(latent_dim)
    n, _ = X.shape
    ids = np.random.choice(n, size=(num_pairs, 2), replace=False)

    V = X[ids][:, 1, :] - X[ids][:, 0, :]

    # cosine similarity
    cs = cosine_similarity(V)
    print cs.shape

    # we want only the lower triangle (excluding the diagonal)
    cs = np.tril(cs, k=-1)
    cs = cs[np.nonzero(cs)]

    score = np.mean(cs)
    hist, _ = np.histogram(cs, bins=np.arange(-1.0, 1.05, 0.1))
    print 'average {}, max {}, min {}'.format(round(score, 2), round(np.amax(cs), 2),  round(np.amin(cs), 2))

if __name__ == '__main__':
    cosine(50)

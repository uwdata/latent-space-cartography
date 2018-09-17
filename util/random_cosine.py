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

from config_glove_6b import dset, dims

# for absolute path
def abs_path (rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)

out = abs_path('../client/data/{}/pairs.h5').format(dset)

# read latent space
def read_ls (latent_dim):
    rawpath = abs_path('../client/data/{}/latent/latent{}.h5'.format(dset, latent_dim))
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])
    return X

# remove previous result
def clean ():
    if os.path.exists(out):
        os.remove(out)

# we want to re-use the same random pairs
def random_pairs (latent_dim, num_pairs=2000):
    X = read_ls(latent_dim)
    n, _ = X.shape
    ids = np.random.choice(n, size=(num_pairs, 2), replace=False)

    with h5py.File(out, 'w') as f:
        f.create_dataset('id', data=ids)
    
    return ids

# pairwise cosine similarity
def cosine (latent_dim, ids):
    X = read_ls(latent_dim)
    V = X[ids][:, 1, :] - X[ids][:, 0, :]

    # cosine similarity
    cs = cosine_similarity(V)

    # we want only the lower triangle (excluding the diagonal)
    cs = np.tril(cs, k=-1)
    cs = cs[np.nonzero(cs)]

    score = np.mean(cs)
    print 'average {}, max {}, min {}, std {}'.format(round(score, 2), \
        round(np.amax(cs), 2),  round(np.amin(cs), 2), round(np.std(cs), 2))

    return cs

# precompute the index and pariwise cosine of the random pairs
# we re-use the same random pairs across all dimensions for consistency
def compute ():
    clean()
    ids = random_pairs(dims[0])

    f = h5py.File(out, 'w')
    for dim in dims:
        cs = cosine(dim, ids)
        f.create_dataset('cosine{}'.format(dim), data=cs)
    
    f.close()

if __name__ == '__main__':
    compute()

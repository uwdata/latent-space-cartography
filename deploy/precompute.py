# -*- coding: utf-8 -*-
# pairwise cosine similarity of random pairs in the latent space

import os
import h5py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# for absolute path
def abs_path (rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)

class RandomCosine (object):
    def __init__ (self, dset, dims):
        self.dset = dset
        self.dims = dims
        self.out = abs_path('./data/{}/pairs.h5').format(dset)

    # read latent space
    def read_ls (self, latent_dim):
        rawpath = abs_path('./data/{}/latent/latent{}.h5'.format(self.dset, latent_dim))
        with h5py.File(rawpath, 'r') as f:
            X = np.asarray(f['latent'])
        return X

    # remove previous result
    def clean (self):
        if os.path.exists(self.out):
            os.remove(self.out)

    # we want to re-use the same random pairs
    def random_pairs (self, latent_dim, num_pairs=2000):
        X = self.read_ls(latent_dim)
        n, _ = X.shape
        ids = np.random.choice(n, size=(num_pairs, 2), replace=False)

        with h5py.File(self.out, 'w') as f:
            f.create_dataset('id', data=ids)
        
        return ids

    # pairwise cosine similarity
    def cosine (self, latent_dim, ids):
        X = self.read_ls(latent_dim)
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
    def compute (self):
        self.clean()
        ids = self.random_pairs(self.dims[0])

        f = h5py.File(self.out, 'w')
        for dim in self.dims:
            cs = self.cosine(dim, ids)
            f.create_dataset('cosine{}'.format(dim), data=cs)
        
        f.close()

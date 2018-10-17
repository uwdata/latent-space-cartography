#!/usr/bin/env python

'''
Run UMAP on the latent dim.
'''

import h5py
import umap
import os
import numpy as np

# dataset config
from config_emoji import *

# path to the stored model
base = '/home/yliu0/data/{}/'.format(dset)

# read latent space
def read_ls (latent_dim):
    # input path
    inpath = base + 'latent/latent{}.h5'.format(latent_dim)
    with h5py.File(inpath, 'r') as f:
        X = np.asarray(f['latent'])
    return X

if __name__ == '__main__':
    for latent_dim in dims:
        print 'Latent dimension: {}'.format(latent_dim)
        # output path
        umap_base = base + 'umap'
        h5_path = base + 'umap/umap{}.h5'.format(latent_dim)

        # remove previous results
        if not os.path.exists(umap_base):
            os.makedirs(umap_base)
        if os.path.exists(h5_path):
            os.remove(h5_path)

        X = read_ls(latent_dim)
        f = h5py.File(h5_path, 'w')

        for n_neighbors in [5, 10, 15, 30, 50]:
            for min_dist in [0.001, 0.01, 0.1, 0.2, 0.5]:
                print 'Neighbors: {}, dist: {}'.format(n_neighbors, min_dist)
                d = umap.UMAP(n_neighbors = n_neighbors, min_dist = min_dist).fit_transform(X)
                name = 'neighbor{}-dist{}'.format(n_neighbors, min_dist)
                f.create_dataset(name, data=d)
        f.close()

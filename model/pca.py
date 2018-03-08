#!/usr/bin/env python

'''
Run PCA on the latent dim.
'''

from sklearn.decomposition import PCA
import h5py
import json
import os

# path to the stored model
base = '/Users/yliu0/data/'

if __name__ == '__main__':
    for latent_dim in [32, 64, 128, 256, 512, 1024]:
        # input path
        inpath = base + 'latent/latent{}.h5'.format(latent_dim)

        # output path
        json_path = base + 'pca/pca{}.json'.format(latent_dim)
        h5_path = base + 'pca/2d{}.h5'.format(latent_dim)

        # remove previous results
        if os.path.exists(h5_path):
            os.remove(h5_path)
        if os.path.exists(json_path):
            os.remove(json_path)

        res = []
        f = h5py.File(inpath, 'r')
        dset = f['latent']

        dim = 2
        pca = PCA(n_components=2)
        # shape: (length, n_components), each point is a float
        d = pca.fit(dset).transform(dset)

        f.close()
        f = h5py.File(h5_path, 'w')
        dset = f.create_dataset('pca', (1, dim), 
                chunks=(1, dim),
                maxshape=(None, dim),
                dtype='float64')

        for i, val in enumerate(d):
            # save hdf5
            dset.resize((i + 1, dim))
            dset[i] = d[i]
            f.flush()

            # save json
            obj = {'x': format(d[i][0], '.3f'), 'y': format(d[i][1], '.3f'), 'i': i}
            res.append(obj)
        
        f.close()

        with open(json_path, 'w') as outfile:
            json.dump(res, outfile)

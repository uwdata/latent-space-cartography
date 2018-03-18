#!/usr/bin/env python

'''
Run t-SNE on the latent dim.
'''

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import h5py
import json
import csv
import os
import time

# path to the stored model
base = '/home/yliu0/data/'

if __name__ == '__main__':
    log = [['Latent Dimensions', 'Perplexity', 'KL Divergence', 'Iterations']]
    for latent_dim in [32, 64, 128, 256, 512, 1024]:
        for perp in [5, 10, 30, 50, 100]:
            # input path
            inpath = base + 'latent/latent{}.h5'.format(latent_dim)

            # output path
            json_path = base + 'tsne/tsne{}_perp{}.json'.format(latent_dim, perp)
            h5_path = base + 'tsne/tsne{}_perp{}.h5'.format(latent_dim, perp)

            # remove previous results
            if os.path.exists(h5_path):
                os.remove(h5_path)
            if os.path.exists(json_path):
                os.remove(json_path)

            res = []
            f = h5py.File(inpath, 'r')
            dset = f['latent']

            dim = 2
            n_iter = 1000
            time_start = time.time()
            print 't-SNE starts! Latent dimensions: {}, perplexity: {}'.format(latent_dim, perp)
            tsne = TSNE(n_components=dim, verbose=1, perplexity=perp, n_iter=n_iter)
            # shape: (length, n_components), each point is a float
            d = tsne.fit_transform(dset)
            print 't-SNE done! Time elapsed: {} s'.format(time.time()-time_start)
            log.append([latent_dim, perp, tsne.kl_divergence_, n_iter])

            f.close()
            f = h5py.File(h5_path, 'w')
            dset = f.create_dataset('tsne', (1, dim), 
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
    
    # write log to CSV
    log_path = base + 'tsne/log{}.csv'.format(int(time.time()) % 100000)
    with open(log_path, 'wb') as csvf:
        wr = csv.writer(csvf)
        wr.writerows(log)

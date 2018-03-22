#!/usr/bin/env python

'''
Run t-SNE on the latent dim.
'''

from sklearn.decomposition import PCA
import model
import os
import h5py
from PIL import Image

# number of PC
pca_dim = 8

# path to the stored model
base = '/Users/yliu0/data/'
outbase = os.path.join(os.path.dirname(__file__), '../client/data/splom/')

if __name__ == '__main__':
    for latent_dim in [32, 64, 128, 256, 512, 1024]:
        print 'Latent Dim: {}'.format(latent_dim)
        # input path
        inpath = base + 'latent/latent{}.h5'.format(latent_dim)

        # PCA
        with h5py.File(inpath, 'r') as f:
            raw = f['latent']
            pca = PCA(n_components = pca_dim)
            d = pca.fit_transform(raw)

        # decoder
        # TODO: fix relative path
        model_base = '../client/data/models/{}/'.format(latent_dim)
        mpath = model_base + 'logo_model_dim={}.json'.format(latent_dim)
        wpath = model_base + 'logo_model_dim={}.h5'.format(latent_dim)
        m = model.Vae(latent_dim = latent_dim)
        vae, encoder, decoder = m.read(mpath, wpath)

        for i in range(pca_dim):
            # TODO: use quartiles
            for j in [-2, -1, 0, 1, 2]:
                point = [0.0] * pca_dim
                point[i] = float(j)
                d[0] = point

                re = pca.inverse_transform(d)
                recon = m.to_image(decoder.predict(re[0:1]))

                img = Image.fromarray(recon, 'RGB')
                img_fn = outbase + 'dim{}_pc{}_{}.png'.format(latent_dim, i, j)
                img.save(img_fn)

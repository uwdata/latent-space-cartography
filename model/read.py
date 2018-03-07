#!/usr/bin/env python

'''
Reads an existing model and output an original/reconstructed image pair.
'''

from __future__ import print_function
import h5py
from PIL import Image
import numpy as np
import os

from keras import backend as K

import model

latent_dim = 32
img_rows, img_cols, img_chns = 64, 64, 3
batch_size = 100

# path to stored models
base = '/Users/yliu0/data/'
rawpath = base + 'logos.hdf5'
resultbase = base + '/logo_result/{}/'.format(latent_dim)
mpath = resultbase + 'logo_model_dim={}.json'.format(latent_dim)
wpath = resultbase + 'logo_model_dim={}.h5'.format(latent_dim)

# load training data
def load_data (fpath, original_img_size):
    f = h5py.File(fpath, 'r')
    dset = f['logos']

    x_train = dset[:15000]
    x_test = dset[15000:]

    x_train = x_train.astype('float32') / 255.
    x_train = x_train.reshape((x_train.shape[0],) + original_img_size)
    x_test = x_test.astype('float32') / 255.
    x_test = x_test.reshape((x_test.shape[0],) + original_img_size)

    return x_train, x_test

# deserialize numpy array to image
def to_image (array):
    array = array.reshape(img_rows, img_cols, img_chns)
    array = 255 * (1.0 - array)
    return array.astype('uint8')

def visualize (x_test, encoder, generator, suffix=''):
    # encode and decode
    x_test_encoded = encoder.predict(x_test, batch_size=batch_size)
    x_test_decoded = generator.predict(x_test_encoded)

    m = 5
    original = np.zeros((img_rows * m, img_cols * m, img_chns), 'uint8')
    reconstructed = np.zeros((img_rows * m, img_cols * m, img_chns), 'uint8')

    def to_image (array):
        array = array.reshape(img_rows, img_cols, img_chns)
        array *= 255
        return array.astype('uint8')

    for i in range(m):
        for j in range(m):
            k = i * m + j
            orig = to_image(x_test[k])
            re = to_image(x_test_decoded[k])
            original[i * img_rows: (i + 1) * img_rows,
                j * img_cols: (j + 1) * img_cols] = orig
            reconstructed[i * img_rows: (i + 1) * img_rows,
                j * img_cols: (j + 1) * img_cols] = re

    img = Image.fromarray(original, 'RGB')
    img.save('{}original.png'.format(imgbase))
    img = Image.fromarray(reconstructed, 'RGB')
    img.save('{}reconstructed_{}.png'.format(imgbase, suffix))

if __name__ == '__main__':
    m = model.Vae(latent_dim = latent_dim)
    vae, encoder, decoder = m.read(mpath, wpath)
    
    x_train, x_test = load_data(rawpath, m.original_img_size)
    visualize(x_test, encoder, decoder)

#!/usr/bin/env python

'''
Reads an existing model and do something.
'''

from __future__ import print_function
import h5py
from PIL import Image
import numpy as np
import os

from keras import backend as K

import model

img_rows, img_cols, img_chns = 64, 64, 3
batch_size = 100

# path to the stored model
base = '/home/yliu0/data/'

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

# run encoder through all points and save as a hdf5 file
# indices should remain the same as raw data
def save_encoded (fn):
    # these will be numpy.ndarray with shape (length, latent_dim)
    x_test_encoded = encoder.predict(x_test, batch_size=batch_size)
    x_train_encoded = encoder.predict(x_train, batch_size=batch_size)
    encoded = np.concatenate((x_train_encoded, x_test_encoded), axis = 0)

    dim = encoded.shape[1]

    # remove previous result
    if os.path.exists(fn):
        os.remove(fn)
    
    f = h5py.File(fn, 'w')
    dset = f.create_dataset('latent', (1, dim), 
            chunks=(1, dim),
            maxshape=(None, dim),
            dtype='float64')
    
    for i, val in enumerate(encoded):
        dset.resize((i + 1, dim))
        dset[i] = encoded[i]
        f.flush()
    
    f.close()

if __name__ == '__main__':
    for latent_dim in [32, 64, 128, 256, 512, 1024]:
        # input path
        rawpath = base + 'logos.hdf5'
        resultbase = base + '/logo_result/{}/'.format(latent_dim)
        mpath = resultbase + 'logo_model_dim={}.json'.format(latent_dim)
        wpath = resultbase + 'logo_model_dim={}.h5'.format(latent_dim)

        # output path
        encode_path = base + 'latent{}.h5'.format(latent_dim)

        m = model.Vae(latent_dim = latent_dim)
        vae, encoder, decoder = m.read(mpath, wpath)
        
        x_train, x_test = load_data(rawpath, m.original_img_size)
        # visualize(x_test, encoder, decoder)
        save_encoded(encode_path)

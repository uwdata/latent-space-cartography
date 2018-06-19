# -*- coding: utf-8 -*-

import sys
import os
import h5py
import numpy as np
from PIL import Image

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

# ugly way to import a file from another directory ...
sys.path.append(os.path.join(os.path.dirname(__file__), '../model'))
import model
from config_emoji import *

base = '/Users/yliu0/data/emoji/'
dims = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
models = {} # re-use keras models

# read raw input
def read_raw ():
    f = h5py.File(base + fn_raw, 'r')
    dset = f[key_raw]

    # shape: (N, 64, 64, 4)
    # value: 8 bit unsigned int in [0, 255]
    return dset

# read latent space
def read_ls (latent_dim):
    rawpath = '{}/latent/latent{}.h5'.format(base, latent_dim)
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])
    return X

# instantiate model
def create_model (latent_dim):
    if latent_dim in models:
        return

    ba = '{}emoji_result/{}/'.format(base, latent_dim)
    mpath = ba + '{}_model_dim={}.json'.format(dset, latent_dim)
    wpath = ba + '{}_model_dim={}.h5'.format(dset, latent_dim)
    m = model.Vae(latent_dim = latent_dim, img_dim=(img_chns, img_rows, img_cols))
    models[latent_dim] = m.read(mpath, wpath) + (m,)

# given a single input in shape (64, 64, 4) with uint8 type
# compute its latent space coordinates
def predict (x, dim):
    create_model(dim)
    vae, encoder, decoder, md = models[dim]
    x_ = np.copy(x).astype('float32') / 255.
    res = encoder.predict(x_.reshape((1,) + x.shape))
    return res[0]

# translate in image space (uint8)
# shift: translate how many pixels
def translate (x, shift = 8):
    down = np.zeros(x.shape, dtype='uint8')
    down[shift:, :, :] = x[0:img_rows-shift, :, :]

    up = np.zeros(x.shape, dtype='uint8')
    up[0:img_rows-shift, :, :] = x[shift:, :, :]

    right = np.zeros(x.shape, dtype='uint8')
    right[:, shift:, :] = x[:, 0:img_cols-shift, :]

    left = np.zeros(x.shape, dtype='uint8')
    left[:, 0:img_cols-shift, :] = x[:, shift:, :]

    #debug
    # img = Image.fromarray(left, img_mode)
    # img.save('translate.png')

    return up, down, left, right

# translate an input, and see how far it deviates from itself in LS
def translate_self ():
    dim = 8
    i = 0
    X = read_raw()
    LS = read_ls(dim)

    trans = translate(X[i])
    for t in trans:
        a = predict(t, dim)
        # compare with its original latent space coordinates
        print round(np.linalg.norm(a - LS[i]), 2)
        print np.around(a - LS[i], decimals=2)

# sample some inputs, apply translation, and plot a histogram
# of how much they deviate
def translate_self_batch ():
    X = read_raw()

    for dim in dims:
        print 'Processing Dim {} ...'.format(dim)
        LS = read_ls(dim)

        res = [[], [], [], []]
        shift = 8
        for i in range(0, train_split, 100):
            trans = translate(X[i], shift)
            for j in range(4):
                a = predict(trans[j], dim)
                d = np.linalg.norm(a - LS[i])
                res[j].append(d)
        
        titles = ['Up', 'Down', 'Left', 'Right']
        f, axarr = plt.subplots(2, 2, sharex='col', sharey='row')
        ax = [axarr[0, 0], axarr[0, 1], axarr[1, 0], axarr[1, 1]]
        for j in range(4):
            ax[j].hist(res[j], 20, facecolor='pink', alpha=0.75)
            if j == 0 or j == 2:
                ax[j].set_ylabel('Count')
            if j == 2 or j == 3:
                ax[j].set_xlabel('L2 Distance to Initial Location')
            ax[j].set_title(titles[j])
        f.suptitle('Latent Dimension {}: Translate {} Pixels'.format(dim, shift))
        plt.savefig('./result/invariant/translate_dim{}_shift{}'.format(dim, shift))

if __name__ == '__main__':
    translate_self_batch()

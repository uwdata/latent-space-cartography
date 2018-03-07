#!/usr/bin/env python

'''
Start training a VAE model.
The model architecture is defined in model.py.
To change hyper-parameters, modify the arguments to model.Vae().
'''

from __future__ import print_function
import h5py
from PIL import Image
import numpy as np
import os

from keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger
from keras.callbacks import Callback, ReduceLROnPlateau
from keras import backend as K

import model

latent_dim = 64

base = '/Users/yliu0/data/'
# input path
inpath = base + 'logos.hdf5'
# output path
outbase = base + '/logo_result/{}/'.format(latent_dim)
# saved model and weights
mpath = outbase + 'logo_model_dim={}.json'.format(latent_dim)
wpath = outbase + 'logo_model_dim={}.h5'.format(latent_dim)
logpath = outbase + 'logo_log_dim={}.csv'.format(latent_dim)

# input image dimensions
img_rows, img_cols, img_chns = 64, 64, 3
epochs = 300
batch_size = 100

'''
 Load training data.
'''
def load_data (fpath):
    f = h5py.File(fpath, 'r')
    dset = f['logos']

    x_train = dset[:15000]
    x_test = dset[15000:]

    return x_train, x_test

'''
 Custom callback to hook into model.fit
'''
class Visualizer(Callback):
    def __init__(self, x_test, encoder, decoder):
        self.x_test = x_test
        self.encoder = encoder
        self.decoder = decoder

    def on_train_end(self, logs={}):
        visualize(self.x_test, self.encoder, self.decoder, 'end')

    def on_epoch_end(self, epoch, logs={}):
        return # turn off
        # every 10 epoch
        if epoch % 10 == 9:
            visualize(self.x_test, self.encoder, self.decoder, epoch + 1)

'''
 Entry point: load data, create model and start training
'''
def train ():
    # initialize our VAE model
    m = model.Vae(latent_dim = latent_dim)
    vae, encoder, generator = m.init_model(mpath, wpath)
    vae.summary()

    # train the VAE on our logo dataset
    original_img_size = m.original_img_size
    x_train, x_test = load_data(inpath)
    x_train = x_train.astype('float32') / 255.
    x_train = x_train.reshape((x_train.shape[0],) + original_img_size)
    x_test = x_test.astype('float32') / 255.
    x_test = x_test.reshape((x_test.shape[0],) + original_img_size)

    print('x_train.shape:', x_train.shape)

    cp = ModelCheckpoint(wpath, save_best_only=True, save_weights_only=True)
    stop = EarlyStopping(monitor='val_loss', patience=20, verbose=0)
    csv_logger = CSVLogger(logpath, append = True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2,
                              patience=5, min_lr=0.001)
    vis = Visualizer(x_test, encoder, generator)
    vae.fit(x_train,
            shuffle=True,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(x_test, None),
            callbacks=[cp, stop, csv_logger, vis])

'''
 Create images of original samples versus reconstructed.
'''
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
    img.save('{}original.png'.format(outbase))
    img = Image.fromarray(reconstructed, 'RGB')
    img.save('{}reconstructed_{}.png'.format(outbase, suffix))

if __name__ == '__main__':
    if not os.path.exists(outbase):
        os.makedirs(outbase)

    train()

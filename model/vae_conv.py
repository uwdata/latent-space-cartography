from __future__ import print_function
import h5py
from PIL import Image
import numpy as np
from scipy.stats import norm
import json
import os

from keras.layers import Input, Dense, Lambda, Flatten, Reshape
from keras.layers import Conv2D, Conv2DTranspose
from keras.models import Model, model_from_json
from keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger
from keras.callbacks import Callback, ReduceLROnPlateau
from keras import backend as K
from keras import metrics

latent_dim = 64

base = '/home/yliu0/data/'
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
# number of convolutional filters to use
filters = 64
# convolution kernel size
num_conv = 3

epochs = 300
batch_size = 100
if K.image_data_format() == 'channels_first':
    original_img_size = (img_chns, img_rows, img_cols)
else:
    original_img_size = (img_rows, img_cols, img_chns)
intermediate_dim = 1024
up_dim = img_rows / 2

def sampling(args):
    epsilon_std = 1.0
    # hack: redefine latent_dim because it's saved in the model
    latent_dim = 64

    z_mean, z_log_var = args
    epsilon = K.random_normal(shape=(K.shape(z_mean)[0], latent_dim),
                              mean=0., stddev=epsilon_std)
    return z_mean + K.exp(z_log_var) * epsilon

'''
 Instantiate the VAE, encoder and decoder model.
'''
def build_model ():
    x = Input(shape=original_img_size, name='input')
    conv_1 = Conv2D(img_chns,
                    kernel_size=(2, 2),
                    padding='same', activation='relu', name='conv_1')(x)
    conv_2 = Conv2D(filters,
                    kernel_size=(2, 2),
                    padding='same', activation='relu', name='conv_2',
                    strides=(2, 2))(conv_1)
    conv_3 = Conv2D(filters,
                    kernel_size=num_conv,
                    padding='same', activation='relu', name='conv_3',
                    strides=1)(conv_2)
    conv_4 = Conv2D(filters,
                    kernel_size=num_conv,
                    padding='same', activation='relu', name='conv_4',
                    strides=1)(conv_3)
    flat = Flatten(name='flat')(conv_4)
    hidden = Dense(intermediate_dim, activation='relu', name='hidden')(flat)

    z_mean = Dense(latent_dim, name='z_mean')(hidden)
    z_log_var = Dense(latent_dim, name='z_log_var')(hidden)

    # note that "output_shape" isn't necessary with the TensorFlow backend
    # so you could write `Lambda(sampling)([z_mean, z_log_var])`
    z = Lambda(sampling, output_shape=(latent_dim,))([z_mean, z_log_var])

    # we instantiate these layers separately so as to reuse them later
    decoder_hid = Dense(intermediate_dim, activation='relu', name='decoder_hid')
    decoder_upsample = Dense(filters * up_dim * up_dim, activation='relu',
                                name='decoder_upsample')

    if K.image_data_format() == 'channels_first':
        output_shape = (batch_size, filters, up_dim, up_dim)
    else:
        output_shape = (batch_size, up_dim, up_dim, filters)

    decoder_reshape = Reshape(output_shape[1:], name='decoder_reshape')
    decoder_deconv_1 = Conv2DTranspose(filters,
                                    kernel_size=num_conv,
                                    padding='same',
                                    strides=1,
                                    activation='relu',
                                    name='decoder_deconv_1')
    decoder_deconv_2 = Conv2DTranspose(filters,
                                    kernel_size=num_conv,
                                    padding='same',
                                    strides=1,
                                    activation='relu',
                                    name='decoder_deconv_2')
    decoder_deconv_3_upsamp = Conv2DTranspose(filters,
                                            kernel_size=(3, 3),
                                            strides=(2, 2),
                                            padding='valid',
                                            activation='relu',
                                            name='decoder_deconv_3_upsamp')
    decoder_mean_squash = Conv2D(img_chns,
                                kernel_size=2,
                                padding='valid',
                                activation='sigmoid',
                                name='decoder_mean_squash')

    hid_decoded = decoder_hid(z)
    up_decoded = decoder_upsample(hid_decoded)
    reshape_decoded = decoder_reshape(up_decoded)
    deconv_1_decoded = decoder_deconv_1(reshape_decoded)
    deconv_2_decoded = decoder_deconv_2(deconv_1_decoded)
    x_decoded_relu = decoder_deconv_3_upsamp(deconv_2_decoded)
    x_decoded_mean_squash = decoder_mean_squash(x_decoded_relu)

    # instantiate VAE model
    vae = Model(x, x_decoded_mean_squash)

    # save model as json
    with open(mpath, 'w') as outfile:
        json.dump(vae.to_json(), outfile)

    # Compute VAE loss
    xent_loss = img_rows * img_cols * metrics.binary_crossentropy(
        K.flatten(x),
        K.flatten(x_decoded_mean_squash))
    kl_loss = - 0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=-1)
    vae_loss = K.mean(xent_loss + kl_loss)
    vae.add_loss(vae_loss)

    vae.compile(optimizer='rmsprop')

    # We also instantiate the encoder and decoder
    # encoder: a model to project inputs on the latent space
    encoder = Model(x, z_mean)

    # decoder: an image generator that can sample from the learned distribution
    decoder_input = Input(shape=(latent_dim,))
    _hid_decoded = decoder_hid(decoder_input)
    _up_decoded = decoder_upsample(_hid_decoded)
    _reshape_decoded = decoder_reshape(_up_decoded)
    _deconv_1_decoded = decoder_deconv_1(_reshape_decoded)
    _deconv_2_decoded = decoder_deconv_2(_deconv_1_decoded)
    _x_decoded_relu = decoder_deconv_3_upsamp(_deconv_2_decoded)
    _x_decoded_mean_squash = decoder_mean_squash(_x_decoded_relu)
    decoder = Model(decoder_input, _x_decoded_mean_squash)

    return vae, encoder, decoder

def recover_encoder (vae):
    x = vae.get_layer('input').input
    z_mean = vae.get_layer('z_mean').output

    return Model(x, z_mean)

def recover_decoder (vae):
    decoder_input = Input(shape=(latent_dim,))
    out = vae.get_layer('decoder_mean_squash').get_output_at(1)

    return Model(x, out)

def recover_generator (vae):
    decoder_hid = vae.get_layer('decoder_hid')
    decoder_upsample = vae.get_layer('decoder_upsample')
    decoder_reshape = vae.get_layer('decoder_reshape')
    decoder_deconv_1 = vae.get_layer('decoder_deconv_1')
    decoder_deconv_2 = vae.get_layer('decoder_deconv_2')
    decoder_deconv_3_upsamp = vae.get_layer('decoder_deconv_3_upsamp')
    decoder_mean_squash = vae.get_layer('decoder_mean_squash')

    decoder_input = Input(shape=(latent_dim,))
    _hid_decoded = decoder_hid(decoder_input)
    _up_decoded = decoder_upsample(_hid_decoded)
    _reshape_decoded = decoder_reshape(_up_decoded)
    _deconv_1_decoded = decoder_deconv_1(_reshape_decoded)
    _deconv_2_decoded = decoder_deconv_2(_deconv_1_decoded)
    _x_decoded_relu = decoder_deconv_3_upsamp(_deconv_2_decoded)
    _x_decoded_mean_squash = decoder_mean_squash(_x_decoded_relu)
    return Model(decoder_input, _x_decoded_mean_squash)

'''
 Load or instantiate the VAE, encoder and decoder mdoels
'''
def init_model (fn, weights):
    try:
        with open(fn, 'r') as infile:
            vae = model_from_json(json.load(infile))
        vae.load_weights(weights)

        # we still have to supply the loss funciton and compile the model
        x = vae.get_layer('input').input
        z_log_var = vae.get_layer('z_log_var').output
        z_mean = vae.get_layer('z_mean').output
        x_decoded_mean_squash = vae.get_layer('decoder_mean_squash').output
        xent_loss = img_rows * img_cols * metrics.binary_crossentropy(
            K.flatten(x),
            K.flatten(x_decoded_mean_squash))
        kl_loss = - 0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=-1)
        vae_loss = K.mean(xent_loss + kl_loss)
        vae.add_loss(vae_loss)
        vae.compile(optimizer='rmsprop')

        encoder = recover_encoder(vae)
        decoder = recover_generator(vae)
        print('Successfully loaded model: {}'.format(mpath))
    except:
        vae, encoder, decoder = build_model()
        print('Instantiating new models ...')

    return vae, encoder, decoder

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
    # train the VAE on our logo dataset
    x_train, x_test = load_data(inpath)

    x_train = x_train.astype('float32') / 255.
    x_train = x_train.reshape((x_train.shape[0],) + original_img_size)
    x_test = x_test.astype('float32') / 255.
    x_test = x_test.reshape((x_test.shape[0],) + original_img_size)

    # initialize our VAE model
    vae, encoder, generator = init_model(mpath, wpath)
    vae.summary()

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

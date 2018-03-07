from __future__ import print_function
import json

from keras.layers import Input, Dense, Lambda, Flatten, Reshape
from keras.layers import Conv2D, Conv2DTranspose
from keras.models import Model, model_from_json
from keras import backend as K
from keras import metrics

def _sampling(args, latent_dim):
    epsilon_std = 1.0

    z_mean, z_log_var = args
    epsilon = K.random_normal(shape=(K.shape(z_mean)[0], latent_dim),
                              mean=0., stddev=epsilon_std)
    return z_mean + K.exp(z_log_var) * epsilon

class Vae(object):
    # filters: number of convolutional filters to use
    # num_conv: convolution kernel size
    def __init__(self, latent_dim = 64, img_dim = (3, 64, 64), batch_size = 100,
         intermediate_dim = 1024, filters = 64, num_conv = 3):
        self.latent_dim = latent_dim
        self.batch_size = batch_size
        self.intermediate_dim = intermediate_dim
        self.filters, self.num_conv = filters, num_conv
        self.img_chns, self.img_cols, self.img_rows = img_dim

        if K.image_data_format() == 'channels_first':
            self.original_img_size = (self.img_chns, self.img_rows, self.img_cols)
        else:
            self.original_img_size = (self.img_rows, self.img_cols, self.img_chns)

    def _loss_function (self, x, z_mean, z_log_var, x_decoded_mean_squash):
        if K.image_data_format() == 'channels_first':
            _, img_chns, img_rows, img_cols = x.shape
        else:
            _, img_rows, img_cols, img_chns = x.shape

        xent_loss = img_rows * img_cols * metrics.binary_crossentropy(
            K.flatten(x),
            K.flatten(x_decoded_mean_squash))
        kl_loss = - 0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=-1)
        vae_loss = K.mean(xent_loss + kl_loss)

    '''
    Instantiate the VAE, encoder and decoder model.
    '''
    def build_model (self, mpath):
        img_chns, img_cols, img_rows = self.img_chns, self.img_cols, self.img_rows
        original_img_size = self.original_img_size
        latent_dim = self.latent_dim
        intermediate_dim = self.intermediate_dim
        up_dim = img_rows / 2
        filters, num_conv = self.filters, self.num_conv
        batch_size = self.batch_size

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
        z = Lambda(_sampling, output_shape=(latent_dim,),
                    arguments={'latent_dim': latent_dim})([z_mean, z_log_var])

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

    def read (self, fn, weights):
        with open(fn, 'r') as infile:
            vae = model_from_json(json.load(infile))
        vae.load_weights(weights)

        # we still have to supply the loss funciton and compile the model
        x = vae.get_layer('input').input
        z_log_var = vae.get_layer('z_log_var').output
        z_mean = vae.get_layer('z_mean').output
        x_decoded_mean_squash = vae.get_layer('decoder_mean_squash').output
        
        # Compute VAE loss
        xent_loss = self.img_rows * self.img_cols * metrics.binary_crossentropy(
            K.flatten(x),
            K.flatten(x_decoded_mean_squash))
        kl_loss = - 0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=-1)
        vae_loss = K.mean(xent_loss + kl_loss)
        vae.add_loss(vae_loss)
        vae.compile(optimizer='rmsprop')

        encoder = self.recover_encoder(vae)
        decoder = self.recover_decoder(vae)

        return vae, encoder, decoder

    def recover_encoder (self, vae):
        x = vae.get_layer('input').input
        z_mean = vae.get_layer('z_mean').output

        return Model(x, z_mean)

    def recover_decoder (self, vae):
        decoder_hid = vae.get_layer('decoder_hid')
        decoder_upsample = vae.get_layer('decoder_upsample')
        decoder_reshape = vae.get_layer('decoder_reshape')
        decoder_deconv_1 = vae.get_layer('decoder_deconv_1')
        decoder_deconv_2 = vae.get_layer('decoder_deconv_2')
        decoder_deconv_3_upsamp = vae.get_layer('decoder_deconv_3_upsamp')
        decoder_mean_squash = vae.get_layer('decoder_mean_squash')

        decoder_input = Input(shape=(self.latent_dim,))
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
    def init_model (self, infile, weights):
        try:
            vae, encoder, decoder = self.read(infile, weights)
            print('Successfully loaded model: {}'.format(weights))
        except:
            vae, encoder, decoder = self.build_model(infile)
            print('Instantiating new models ...')

        return vae, encoder, decoder

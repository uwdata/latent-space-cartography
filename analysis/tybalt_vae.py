# -*- coding: utf-8 -*-
""" 
1. Replicate some of the sanity checks in tybalt_vae.ipynb
2. Extracting decoder weights as in extract_tybalt_weights.ipynb

Note that Tybalt uses python version 3.5
The associated environment can be activated via:
    conda activate tybalt
"""

import os
import csv
import h5py
import numpy as np

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

base = '/Users/yliu0/code/tybalt/'
# input data before training
p_raw = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq.tsv')
out_raw = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq.h5')
out_header = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq_header.csv')
# latent coordinates
p_latent = os.path.join(base, 'data', 'encoded_rnaseq_onehidden_warmup_batchnorm.tsv')
# Keras model
p_encoder_model = os.path.join(base, 'models', 'encoder_onehidden_vae.hdf5')
p_decoder_model = os.path.join(base, 'models', 'decoder_onehidden_vae.hdf5')
# decoder weights
p_decoder_weights = os.path.join(base, 'results', 'tybalt_gene_weights.tsv')

# read latent space coordinates as a numpy array
def read_ls ():
    res = []
    with open(p_latent, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            if row[1] == '1' and row[2] == '2':
                continue # discard header row
            res.append(row[1:]) # discard the first column, which is some ID
    res = np.asarray(res, dtype=np.float32)

    # shape: (10459, 100)
    return res

# reading TSV is so freaking slow
# convert to hdf5
def convert_raw ():
    res = []
    with open(p_raw, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            res.append(row[1:]) # discard the first column, which is some ID
    header = res[0]
    res = np.asarray(res[1:], dtype=np.float32)
    print('Done reading.')

    # save header seperately because it's difficult to get h5py work with strings
    with open(out_header, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(header)

    # save numbers to hdf5
    f = h5py.File(out_raw, 'w')
    dset = f.create_dataset('data', data=res)
    f.close()

    return res

# read the raw input data as a numpy array
def read_raw ():
    f = h5py.File(out_raw, 'r')
    X = f['data'][:]
    f.close()

    # shape: (10459, 5000)
    return X

# sum along each latent dimension, and print the largest / smallest
def sum_dim (X):
    # obviously, neither the sum nor the dim # agree with the notebook
    # did they save the output file from a seperate run??
    agg = np.sum(X, axis = 0)
    ids = np.argsort(agg)
    print('Top 10 most active nodes:')
    # note that their latent feature index starts from 1!
    for i in range(1, 11):
        print(ids[-i] + 1, agg[ids[-i]])
    print('Top 10 least active nodes:')
    for i in range(10):
        print(ids[i] + 1, agg[ids[i]])

# histogram of node activity for all 100 latent features
def sum_dim_hist (X):
    # the histogram looks sufficiently different, too
    # the LS file is definitely from another run
    agg = np.sum(X, axis = 0)
    plt.figure()
    plt.hist(agg)
    plt.xlabel('Activation Sum')
    plt.ylabel('Count')
    plt.savefig('./result/node_activity.png')

# read the weight matrix of the single-layer decoder
def read_decoder_weights ():
    # move import statement here because it's slow
    from keras.models import load_model
    decoder = load_model(p_decoder_model)
    weights = []
    for layer in decoder.layers:
        weights.append(layer.get_weights())
    weight_layer = weights[1][0]

    # shape (100, 5000)
    return weight_layer

# read the decoder weights from a tsv file
def read_decoder_weights_tsv ():
    res = []
    with open(p_decoder_weights, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            res.append(row[1:])
    res = np.asarray(res[1:], dtype=float)
    # print(res[1][:10])
    return res

# check if reconstructing z to output is simply multiplying decoder weight
# the recon. error magnitude is way off, so it seems the above statement is false
def reconstruct (z, W, X):
    recon = np.dot(z, W)
    compare_reconstructed(X, recon)

def compare_reconstructed (X, recon):
    n, _ = X.shape
    diff = np.mean(recon - X, axis=0)
    diff_abs = np.sum(np.abs(recon - X), axis=0) / n
    ids = np.argsort(diff_abs)

    # gene name
    header = []
    with open(out_header, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            header = row

    print('name', 'gene mean', 'gene abs(sum)')
    for i in range(1, 6):
        index = ids[-i]
        print(header[index], diff[index], diff_abs[index])

# read the decoder model
def read_decoder ():
    from keras.models import load_model
    decoder = load_model(p_decoder_model)
    # decoder.summary()
    return decoder

# reconstruct output from z, and compare with input
# the gene names match perfectly, and errors match up to 3 decimal points
def reconstruct_2 (z, decoder, X):
    recon = decoder.predict(z)
    compare_reconstructed(X, recon)

# compare the decoder weights:
# (1) recover from decoder model
# (2) read directly from TSV
def compare_weights ():
    W = read_decoder_weights()
    W_ = read_decoder_weights_tsv()
    diff_abs = np.sum(np.abs(W - W_), axis=1)
    print(np.max(diff_abs))

if __name__ == '__main__':
    compare_weights()

# -*- coding: utf-8 -*-
""" Replicate some of the sanity checks in tybalt_vae.ipynb
Note that Tybalt uses python version 3.5
The associated environment can be activated via:
    conda activate tybalt
"""

import os
import csv
import numpy as np

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

base = '/Users/yliu0/code/tybalt/'
# input data before training
p_raw = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq.tsv.gz')
# latent coordinates
p_latent = os.path.join(base, 'data', 'encoded_rnaseq_onehidden_warmup_batchnorm.tsv')
# Keras model
p_encoder_model = os.path.join(base, 'models', 'encoder_onehidden_vae.hdf5')
p_decoder_model = os.path.join(base, 'models', 'decoder_onehidden_vae.hdf5')

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

# sum along each latent dimension, and print the largest / smallest
def sum_dim (X):
    # obviously, neither the sum nor the dim # agree with the notebook
    # did they save the output file from a seperate run??
    agg = np.sum(X, axis = 0)
    ids = np.argsort(agg)
    print('Top 10 most active nodes:')
    for i in range(1, 11):
        print(ids[-i], agg[ids[-i]])
    print('Top 10 least active nodes:')
    for i in range(10):
        print(ids[i], agg[ids[i]])

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

if __name__ == '__main__':
    LS = read_ls()
    sum_dim_hist(LS)

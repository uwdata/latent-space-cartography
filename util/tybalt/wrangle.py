# -*- coding: utf-8 -*-

import os
import csv
import h5py
import numpy as np
from shutil import copyfile

base = '/Users/yliu0/code/tybalt/'
p_latent = os.path.join(base, 'data', 'encoded_rnaseq_onehidden_warmup_batchnorm.tsv')
p_raw = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq.h5')
out_base = '/Users/yliu0/data/tybalt/'
out_latent = os.path.join(out_base, 'latent/latent100.h5')
out_raw = os.path.join(out_base, 'raw.h5')

# read tsv, discarding (optionally) the first row and (optionally) the first column
def read_tsv (fn, dtype=float, col_start=1, row_start=1):
    res = []
    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            res.append(row[col_start:])
    res = np.asarray(res[row_start:], dtype=dtype)
    return res

def convert_ls ():
    res = read_tsv(p_latent)

    f = h5py.File(out_latent, 'w')
    dset = f.create_dataset('latent', data=res)
    f.close()

def copy_raw ():
    copyfile(p_raw, out_raw)

if __name__ == '__main__':
    # convert_ls()
    copy_raw()

# -*- coding: utf-8 -*-

import os
import csv
import h5py
import numpy as np

class Util(object):
    def __init__(self):
        base = '/Users/yliu0/code/tybalt/'
        self.base = base
        # input data before training
        self.p_raw = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq.h5')
        # latent coordinates
        self.p_latent = os.path.join(base, 'data', 'encoded_rnaseq_onehidden_warmup_batchnorm.tsv')
        # meta data
        self.p_header = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq_header.csv')
        self.p_id = os.path.join(base, 'data', 'patient_id.csv')
        self.p_meta = os.path.join(base, 'data', 'ov_subtype_info.tsv')

    # read tsv, discarding the first row and first column
    def read_tsv (self, fn, dtype=float):
        res = []
        with open(fn, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            for row in reader:
                res.append(row[1:])
        res = np.asarray(res[1:], dtype=dtype)
        return res

    # read csv that contain only one row (typically meta data)
    def read_csv_single (self, fn):
        res = []
        with open(fn, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                res = row
        return np.asarray(res)

    # read latent space
    def read_ls (self):
        return self.read_tsv(self.p_latent)

    # read the raw input data as a numpy array
    def read_raw (self):
        f = h5py.File(self.p_raw, 'r')
        X = f['data'][:]
        f.close()

        # shape: (10459, 5000)
        return X

    # read the 5000 gene names
    def read_header (self):
        return self.read_csv_single(self.p_header)

    # read the 10459 patient IDs
    def read_id (self):
        return self.read_csv_single(self.p_id)

    # read the meta data (see hgsc_subtypes_tybalt.ipynb for schema)
    def read_meta (self):
        return self.read_tsv(self.p_meta, str)

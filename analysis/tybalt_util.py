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
        # saved model
        self.p_decoder_model = os.path.join(base, 'models', 'decoder_onehidden_vae.hdf5')
        # meta data
        self.p_header = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq_header.csv')
        self.p_id = os.path.join(base, 'data', 'patient_id.csv')
        self.p_meta = os.path.join(base, 'data', 'ov_subtype_info.tsv')
        self.p_clinical = os.path.join(base, 'data', 'tybalt_features_with_clinical.tsv')
        # schema index in the meta table
        self.i_subtype = 2

    # read tsv, discarding (optionally) the first row and (optionally) the first column
    def read_tsv (self, fn, dtype=float, col_start=1, row_start=1):
        res = []
        with open(fn, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            for row in reader:
                res.append(row[col_start:])
        res = np.asarray(res[row_start:], dtype=dtype)
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
        return self.read_tsv(self.p_meta, str, 0)

    # read more meta data
    def read_clinical (self):
        res = self.read_tsv(self.p_clinical, str, 0)
        n = res.shape[0]
        return np.concatenate((res[:, 0].reshape(n, 1), res[:, 101:]), axis=1)

    # read the decoder model
    def read_decoder (self):
        from keras.models import load_model
        decoder = load_model(self.p_decoder_model)
        # decoder.summary()
        return decoder

    def right_outer_join (self, left, right):
        # convert left to a dictionary
        lookup = {}
        for i in range(left.shape[0]):
            lookup[left[i]] = i

        # right outer join
        ids = []
        for i in range(len(right)):
            if right[i] in lookup:
                ids.append([i, lookup[right[i]]])

        # each row is [index in right, index in left]
        return np.asarray(ids, dtype=int)

    # get the indices of right outer join of meta with patient ID
    def join_meta (self):
        pid = self.read_id()
        meta = self.read_meta()[:, 0]
        ids = self.right_outer_join(meta, pid)

        # shape: (295, 2)
        return ids

    # get the indices in input array that has a certain subtype
    def subtype_group (self, meta, ids, subtype):
        res = []
        for tup in ids:
            if meta[tup[1]][self.i_subtype] == subtype:
                res.append(tup[0])
        return np.asarray(res, dtype=int)

    # compute the average inter-point distance (L2) between each point pair
    def _pointwise_dist (self, X, Y=None):
        R = X if Y is None else Y
        m, _ = X.shape
        n, _ = R.shape

        s = 0
        for i in range(m):
            # left hand matrix: repeat an element N times
            L = np.repeat([X[i]], n, axis=0)
            D = np.linalg.norm(L - R, axis=1)
            # for intra-cluster distance, exclude self
            denom = n - 1 if Y is None else n
            s += np.sum(D) / float(denom)
        
        return s / float(m)

    # a score representing how tight a cluster is
    def cluster_score (self, ids, X):
        a = self._pointwise_dist(X[ids])
        b = self._pointwise_dist(X[ids], np.delete(X, ids, axis=0))
        print('Intra-cluster distance: {}, Inter-cluster distance: {}'.format(a, b))
        score = (b - a) / max(a, b)
        return score

# -*- coding: utf-8 -*-

import os
import h5py
import csv
import numpy as np

base = '/Users/yliu0/data/emoji/'

# for absolute path
def abs_path (rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)

# read latent space
def read_ls (latent_dim):
    rawpath = '{}/latent/latent{}.h5'.format(base, latent_dim)
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])
    return X

def read_meta ():
    res = []
    with open(base + 'database.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[0] == 'index':
                continue # skip header
            # i, category, name, platform, version, codepoints, shortcode
            res.append(row[0:5] + row[7:9])
    return res

def group_by (meta, col):
    res = {}

    for row in meta:
        c = row[col]
        i = int(row[0])
        if c in res:
            res[c].append(i)
        else:
            res[c] = [i]
    
    return res

# deprecated
# turns out creating a giant matrix is a bad idea ...
def pointwise_dist_dep (X):
    n, latent_dim = X.shape

    # prepare matrices
    L = np.empty([0, latent_dim])
    R = np.empty([0, latent_dim])
    for i in range(n):
        # left hand matrix: repeat an element N times
        L = np.concatenate((L, np.repeat([X[i]], n, axis=0)), axis=0)

        # right hand matrix: every element
        R = np.concatenate((R, X), axis=0)
    
    # compute distance
    D = np.linalg.norm(L-R, axis=1)

    # take average
    d = np.sum(D) / float(n * (n-1))
    return d

# compute the average inter-point distance (L2) between each point pair
def pointwise_dist (X):
    n, latent_dim = X.shape

    s = 0
    for i in range(n):
        # left hand matrix: repeat an element N times
        L = np.repeat([X[i]], n, axis=0)
        D = np.linalg.norm(L - X, axis=1)
        s += np.sum(D) / float(n - 1)
    
    return s / float(n)

# print the global average pointwise distance for each latent dim
def report_baseline ():
    dims = [32, 64, 128, 256, 512, 1024]
    for dim in dims:
        X = read_ls(dim)
        # running over all points will take too long, so we just go for a sample
        # -- how accurate is this approximation?
        # -- 8.377 (all points) vs 8.530 (first 1000) in dim=32
        dist = pointwise_dist(X[0:1000])
        print 'Latent Dimension: {}'.format(dim)
        print 'Average point-wise distance: {}'.format(dist)

# produce a csv of intra-cluster distances of clusters defined in groups
def report_cluster (X, groups, out):
    res = []
    for k in groups.keys():
        if k == '':
            continue # skip empty key
        dist = pointwise_dist(X[groups[k]])
        res.append([k, dist])

    # sort by intra-cluster distance
    res.sort(key = lambda x : x[1])

    with open('./{}'.format(out), 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for row in res:
            writer.writerow(row)

if __name__ == '__main__':
    meta = read_meta()
    codes = group_by(meta, 6) # 6 is the column for shortcode
    dim = 1024
    X = read_ls(dim)
    report_cluster(X, codes, 'shortcode_{}.csv'.format(dim))

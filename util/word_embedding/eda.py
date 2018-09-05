# -*- coding: utf-8 -*-

import os
import csv
import h5py
import numpy as np
from sklearn.neighbors import KDTree
from sklearn import preprocessing

test = '/Users/yliu0/data/word/benchmarks/questions-words.txt'
base = '/Users/yliu0/data/glove_6b/'

# read the mapping between index and word
def read_meta ():
    with open(base + 'meta300.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        res = [] # forward mapping of i to word
        rev = {} # reverse mapping of word to i
        for row in reader:
            if row[0] == 'i':
                continue
            res.append(row)
            rev[row[1]] = int(row[0])
    return res, rev

# read the analogy test set
def read_test ():
    with open(test, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        groups = []
        res = []
        group = []
        for row in reader:
            if row[0] == ':':
                groups.append(row[1])
                if len(group):
                    res.append(group)
                    group = []
            else:
                group.append(row)
        res.append(group)

    # res: 14 x 4, where 14 is # of groups, 4 is each test
    # groups: 14, contains the name of the groups
    return res, groups

# remove words not in the embedding
def clean_test (words, lookup):
    res = []
    idx = []
    first = ''
    for g in words:
        # break into pairs
        pairs = []
        for line in g:
            line = [s.lower() for s in line]
            if first == '':
                first = line[0]
                if line[0] in lookup and line[1] in lookup:
                    pairs.append(line[:2])
            if first == line[0]:
                if line[2] in lookup and line[3] in lookup:
                    pairs.append(line[2:])
            else:
                first = ''
                break
        res.append(pairs)

        # convert to indices
        tmp = []
        for p in pairs:
            tmp.append([lookup[p[0]], lookup[p[1]]])
        idx.append(np.asarray(tmp, dtype=int))

    # res: 14 x 2, where 14 is # of groups, 2 is each pair of word
    # idx: 14 x 2, where 14 is # of groups, 2 is each pair of indices
    return res, idx

# read latent space
def read_ls (latent_dim):
    rawpath = base + 'latent/latent{}.h5'.format(latent_dim)
    with h5py.File(rawpath, 'r') as f:
        X = np.asarray(f['latent'])
    return X

def convert_pairs (pairs):
    res = []
    for p in pairs:
        for pp in pairs:
            if p[0] != pp[0]:
                res.append([p[0], p[1], pp[0], pp[1]])
    return np.asarray(res, dtype=int)

def analogy (X, pairs, exclude_b=True):
    test = convert_pairs(pairs)
    x = X[test]
    v = - x[:, 0] + x[:, 1] + x[:, 2]

    # build KD tree
    tree = KDTree(preprocessing.normalize(X))
    _, idx = tree.query(v, k=2)

    correct = 0
    total = idx.shape[0]
    for j in range(total):
        nns = idx[j]
        nn = nns[1] if exclude_b and nns[0] == test[j][2] else nns[0]
        if nn == test[j][3]:
            correct += 1

    percent = round(float(correct)/total, 3) * 100
    print '{}% ({}/{})'.format(percent, correct, total)

if __name__ == '__main__':
    words, groups = read_test()
    meta, lookup = read_meta()
    words, idx = clean_test(words, lookup)

    dim = 100
    X = read_ls(dim)
    analogy(X, idx[0])

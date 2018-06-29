# -*- coding: utf-8 -*-
""" 
1. Replicate the results in hgsc_subtypes_tybalt.ipynb

Note that Tybalt uses python version 3.5
The associated environment can be activated via:
    conda activate tybalt
"""
import os
import numpy as np
from sklearn.svm import LinearSVC
from tybalt_util import Util

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

# our helper class
util = Util()

# index
i_gender = 14
node = 82 - 1 # Tybalt's index starts from 1

# file paths
p_decoder_weights = os.path.join(util.base, 'results', 'tybalt_gene_weights.tsv')

def get_sex_groups ():
    meta = util.read_clinical()
    pid = util.read_id()
    ids = util.right_outer_join(meta[:, 0], pid)

    names = ['female', 'male']
    groups = [sex_group(meta, ids, name) for name in names]
    print('{} females, {} males'.format(groups[0].shape[0], groups[1].shape[0]))
    return groups

def sex_group (meta, ids, which):
    res = []
    for tup in ids:
        if meta[tup[1]][i_gender] == which:
            res.append(tup[0])
    return np.asarray(res, dtype=int)

# verify if encoding 82 separates sex
def plot_dim_sex ():
    z = util.read_ls()
    indices = get_sex_groups()
    data =[z[i, node] for i in indices]

    plt.figure()
    for i in range(len(data)):
        color = 'pink' if i == 0 else 'lightblue'
        label = 'Female' if i == 0 else 'Male'
        plt.hist(data[i], 20, facecolor=color, alpha=0.5, label=label)

    plt.title('Sex and Encoding 82')
    plt.xlabel('Encoding 82')
    plt.legend()
    plt.ylabel('Count')
    plt.savefig('./result/sex_dim82.png')

# get the top sex differentiating genes using their approach
def naive_sex ():
    w = util.read_tsv(p_decoder_weights)[node, :]
    top = np.argsort(np.abs(w))
    header = util.read_header()
    print('Top 20 genes differentiating sex:')
    w = np.around(w, decimals=4)
    for i in range(1, 21):
        idx = top[-i]
        print('{}\t{}'.format(header[idx], w[idx]))

# linear svm separating female and male
def svm_sex ():
    z = util.read_ls()
    decoder = util.read_decoder()
    ids = get_sex_groups()

    # prepare data and class labels
    X = np.concatenate((z[ids[0], :], z[ids[1], :]), axis=0)
    y = np.zeros(X.shape[0], dtype=int)
    y[ids[0].shape[0]:] = 1 # 0 - female, 1 - male

    # svm
    clf = LinearSVC()
    clf.fit(X, y)
    w = clf.coef_[0] # weights
    w0 = clf.intercept_

    # see if the classes are perfectly separated
    y_ = clf.predict(X)
    acc = 1 - np.count_nonzero(y - y_) / float(X.shape[0])
    print('SVM accuracy: {}'.format(acc))

    # see if the normal vector is similar to their sex seperating feature
    ve = np.zeros(100, dtype=float)
    ve[node] = 1.0
    dist = np.dot(w, ve) / np.linalg.norm(w)
    print('Cosine distance between w and axis 82: {}'.format(dist))

    # the hyperplane is: w0 + w * x = 0
    # thus w is a normal vector for the plane
    # but how do we find the genes that vary most along this vector?
    probe = np.asarray([w, -w])
    genes = decoder.predict(probe)
    diff = genes[0] - genes[1]
    top = np.argsort(np.abs(diff))
    header = util.read_header()
    print('Top 20 genes differentiating sex:')
    for i in range(1, 21):
        idx = top[-i]
        print('{}\t{}'.format(header[idx], diff[idx]))

if __name__ == '__main__':
    svm_sex()

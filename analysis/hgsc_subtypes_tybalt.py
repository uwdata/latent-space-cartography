# -*- coding: utf-8 -*-
""" 
1. Replicate the results in hgsc_subtypes_tybalt.ipynb

Note that Tybalt uses python version 3.5
The associated environment can be activated via:
    conda activate tybalt
"""
import os
import csv
import numpy as np
from scipy.stats import skew, skewtest
from tybalt_util import Util

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

# our helper class
util = Util()

# file paths
p_mesen = os.path.join(util.base, 'results', 'hgsc_node87genes_pos.tsv')
p_immun = os.path.join(util.base, 'results', 'hgsc_node87genes_neg.tsv')
p_mesen2 = os.path.join(util.base, 'results', 'hgsc_node56genes_neg.tsv')
p_immun2 = os.path.join(util.base, 'results', 'hgsc_node56genes_pos.tsv')

# wrangling the patient ID data - save to a CSV file
def save_id ():
    res = []
    with open(util.p_latent, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            if row[1] == '1' and row[2] == '2':
                continue # discard header row
            res.append(row[0])
    out = os.path.join(util.base, 'data', 'patient_id.csv')
    with open(out, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(res)

# wrangle result file to be in WebGestalt required format
def wrangle_gene_list ():
    ps = [p_mesen, p_immun, p_mesen2, p_immun2]
    out = [
        'hgsc_node87genes_pos.txt',
        'hgsc_node87genes_neg.txt',
        'hgsc_node56genes_neg.txt',
        'hgsc_node56genes_pos.txt'
    ]
    for i in range(4):
        data = util.read_tsv(ps[i], str, 0)[:, 0]
        fn = os.path.join(util.base, 'results', out[i])
        with open(fn, 'w', newline='') as f:
            writer = csv.writer(f)
            for d in data:
                writer.writerow([d])

# save gene list to txt file, with one gene per row
def save_gene_list (data, fn):
    fn = os.path.join(util.base, 'results', fn)
    with open(fn, 'w', newline='') as f:
        writer = csv.writer(f)
        for d in data:
            writer.writerow([d])

# replicate the result in hgsc_subtypes_tybalt.ipynb, Out[9]
def subtype_mean ():
    # get the indices of the four subtypes
    meta = util.read_meta()
    ids = util.join_meta()
    names = ['Differentiated', 'Immunoreactive', 'Mesenchymal', 'Proliferative']
    groups = [util.subtype_group(meta, ids, name) for name in names]

    # aggregate LS based on types
    z = util.read_ls()
    z_agg = []
    for g in groups:
        z_agg.append(np.mean(z[g], axis=0))
    z_agg = np.asarray(z_agg, dtype=float)

    # pretty print
    for i in range(4):
        print('{} {}'.format(names[i], np.around(z_agg[i, :10], decimals=3)))
    
    return z_agg

# turn array into a dictionary
def arr_to_dict (arr):
    res = {}
    for i in arr:
        res[i] = 1
    return res

# read their genes about mesen and immuno subtypes
def im_genes ():
    ps = [p_mesen, p_mesen2, p_immun, p_immun2]
    genes = [util.read_tsv(p, str, 0)[:, 0] for p in ps]

    mesen = np.concatenate((genes[0], genes[1]))
    immun = np.concatenate((genes[2], genes[3]))

    return arr_to_dict(mesen), arr_to_dict(immun)

# helper function used by im_vector()
def compare_results (ids, arr, header, lookup):
    count = 0
    for i in ids:
        gene = header[i]
        if (gene in lookup):
            # print('{}\t{}'.format(gene, arr[i]))
            count += 1
    print('Total: {}/{}'.format(count, ids.shape[0]))

# decode the centroid of mesen or immuno group, and find the max diff genes
# compare our gene list with their list
def im_vector ():
    # get the indices of the two subtypes
    header = util.read_header()
    meta = util.read_meta()
    ids = util.join_meta()
    names = ['Mesenchymal', 'Immunoreactive']
    groups = [util.subtype_group(meta, ids, name) for name in names]

    # compute centroid
    z = util.read_ls()
    means = np.asarray([np.mean(z[g], axis=0) for g in groups], dtype=float)

    # decode centroid
    decoder = util.read_decoder()
    genes = decoder.predict(means)
    diff = genes[0] - genes[1] # mesenchymal - immunoreactive

    # histogram of diff
    plt.figure()
    plt.hist(diff, 20, facecolor='pink', alpha=0.75)
    plt.title('Mesenchymal - Immunoreactive')
    plt.xlabel('Gene expression diff')
    plt.ylabel('Count')
    plt.savefig('./result/mesen-immuno-diff.png')

    # transform right-skewed data
    print('Skewness: {}'.format(skew(diff)))
    # make the data positive before taking square root
    diff = np.sqrt(diff - diff.min())
    print('Skewness after transformation: {}'.format(skew(diff)))
    print(skewtest(diff))

    # plot again
    plt.figure()
    plt.hist(diff, 20, facecolor='pink', alpha=0.75)
    plt.title('Mesenchymal - Immunoreactive')
    plt.xlabel('Gene expression diff, after transformation sqrt(x - min(x))')
    plt.ylabel('Count')
    plt.savefig('./result/mesen-immuno-transformed.png')

    # # what if I directly compute the mean of input genes?
    # raw = util.read_raw()
    # raw_genes = np.asarray([np.mean(raw[g], axis=0) for g in groups], dtype=float)
    # raw_diff = raw_genes[0] - raw_genes[1] # mesenchymal - immunoreactive
    # raw_srt = np.argsort(raw_diff)
    # print('Comparing with raw')
    # compare_results(srt[:300], diff, header, arr_to_dict(header[raw_srt[:300]]))
    # compare_results(srt[-300:], diff, header, arr_to_dict(header[raw_srt[-300:]]))

    # # compare
    # mesen, immun = im_genes()
    # print('Immunoreactive')
    # compare_results(srt[:300], diff, header, immun)
    # print('Mesenchymal')
    # compare_results(srt[-300:], diff, header, mesen)

    # output our "high weight genes"
    pos, neg = high_weight_genes(diff, header, 2.5)
    save_gene_list(pos, 'mesenchymal_genes_sd.txt')
    save_gene_list(neg, 'immunoreactive_genes_sd.txt')
    print('Totol genes 2.5 standard deviation away:')
    print('{} mesenchymal, {} immunoreactive'.format(len(pos), len(neg)))

    # # output the top / bottom N genes
    # srt = np.argsort(diff)
    # cutoff = 150
    # save_gene_list(header[srt[:cutoff]], 'immunoreactive_genes_{}.txt'.format(cutoff))
    # save_gene_list(header[srt[-cutoff:]], 'mesenchymal_genes_{}.txt'.format(cutoff))

def high_weight_genes (w, header, highsd=2):
    sd = np.std(w)
    mean = np.mean(w)
    print('Mean: {}, SD: {}'.format(mean, sd))
    pos = []
    neg = []
    for i in range(header.shape[0]):
        if w[i] > mean + highsd * sd:
            pos.append(header[i])
        if w[i] < mean - highsd * sd:
            neg.append(header[i])
    return pos, neg

# like im_vector, but don't do the diff
def im_mean ():
    # get the indices of the two subtypes
    header = util.read_header()
    meta = util.read_meta()
    ids = util.join_meta()
    names = ['Mesenchymal', 'Immunoreactive']
    groups = [util.subtype_group(meta, ids, name) for name in names]

    # compute centroid
    z = util.read_ls()
    means = np.asarray([np.mean(z[g], axis=0) for g in groups], dtype=float)

    # decode centroid
    decoder = util.read_decoder()
    genes = decoder.predict(means)
    save_gene_list(high_weight_genes(genes[0], header)[0], 'mesenchymal_genes.txt')
    save_gene_list(high_weight_genes(genes[1], header)[0], 'immunoreactive_genes.txt')

# cluster quality of mesen or immuno type
def im_vector_quality ():
    # get the indices of the two subtypes
    meta = util.read_meta()
    ids = util.join_meta()
    names = ['Mesenchymal', 'Immunoreactive']
    groups = [util.subtype_group(meta, ids, name) for name in names]

    z = util.read_ls()
    # X = util.read_raw()
    for i in range(2):
        score = util.cluster_score(groups[i], z)
        # score = util.cluster_score(groups[i], X)
        print('{}: {}%'.format(names[i], int(score * 100)))

if __name__ == '__main__':
    im_vector()

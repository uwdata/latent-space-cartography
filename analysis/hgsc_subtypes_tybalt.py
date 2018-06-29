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

if __name__ == '__main__':
    mesen, immun = im_genes()
    print('CA4' in mesen, 'CA4' in immun)

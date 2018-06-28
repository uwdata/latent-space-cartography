# -*- coding: utf-8 -*-
""" 
1. Replicate the results in hgsc_subtypes_tybalt.ipynb

Note that Tybalt uses python version 3.5
The associated environment can be activated via:
    conda activate tybalt
"""
import numpy as np
from tybalt_util import Util

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

# our helper class
util = Util()

# index
i_gender = 14

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
    col = 82 - 1 # Tybalt's index starts from 1
    z = util.read_ls()
    indices = get_sex_groups()
    data =[z[i, col] for i in indices]

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

if __name__ == '__main__':
    plot_dim_sex()

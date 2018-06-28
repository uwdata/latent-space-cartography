# -*- coding: utf-8 -*-
""" 
1. Replicate the results in hgsc_subtypes_tybalt.ipynb

Note that Tybalt uses python version 3.5
The associated environment can be activated via:
    conda activate tybalt
"""
import numpy as np
from tybalt_util import Util

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

if __name__ == '__main__':
    get_sex_groups()

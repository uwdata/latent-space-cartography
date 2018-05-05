#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Recover images from HDF5 file, with image names matching the indices
'''

import h5py
from PIL import Image

base = '/Users/yliu0/data/'
rawpath = base + 'logos.hdf5'
imgbase = base + '/logos/'

if __name__ == '__main__':
    f = h5py.File(rawpath, 'r')
    dset = f['logos']

    for i, arr in enumerate(dset):
        img = Image.fromarray(arr, 'RGB')
        img.save(imgbase + '{}.jpg'.format(i))

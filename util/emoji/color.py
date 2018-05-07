# -*- coding: utf-8 -*-
# generate a CSV file of meta data to be imported into MySQL

import os
import csv
import numpy as np
import h5py
from PIL import Image

dset = 'emoji'

base = '/Users/yliu0/data/{}/'.format(dset)
img_base = base + 'images/'
h5 = base + '{}.h5'.format(dset)
out = base + 'color.csv'

img_rows, img_cols = 64, 64

# given an image uint array of shape (w, h, channel)
# return a single hex color
def average_color (arr):
    num_chns = 3
    # discard alpha channel
    arr = arr[:, :, :num_chns]

    arr = arr.reshape((img_rows * img_cols, num_chns))
    avg = np.floor(np.mean(arr, axis = 0))
    # get the hex code
    code = ''
    for index, x in np.ndenumerate(avg):
        c = hex(x)[2:-1] # remove '0x' at the beginning
        c += '0' if len(c) == 1 else '' # if number is single digit, pad with 0
        code += c
    return '#' + code

def better_average_color (img):
    x = np.array(img)
    r, g, b, a = np.rollaxis(x, axis = -1)
    r[a == 0] = 255
    g[a == 0] = 255
    b[a == 0] = 255

    return average_color(x)

# compute mean color from the data array
def gen_mean_color ():
    f = h5py.File(h5, 'r')
    data = f[dset]

    n = data.shape[0]
    with open(out, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')

        for i in range(n):
            color = average_color(np.asarray(data[i], dtype=np.uint8))
            writer.writerow([i, color])
    
    f.close()

# compute mean color from image, so we can handle alpha mask properly
def gen_better_mean_color ():
    count = 0
    d = {}

    for f in os.listdir(img_base):
        i, ext = os.path.splitext(f)

        # ignore weird hidden files
        if ext != '.png':
            continue

        img = Image.open(img_base + f).convert('RGBA')
        color = better_average_color(img)
        img.close()
        count += 1
        d[int(i)] = color

    with open(out, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        for j in range(count):
            writer.writerow([j, d[j]])

if __name__ == '__main__':
    # gen_mean_color()
    gen_better_mean_color()

# -*- coding: utf-8 -*-
# recover the image file names and meta data for indices

import os
import h5py
import csv
from PIL import Image

base = '/Users/yliu0/data/'
merged = os.path.join(os.path.dirname(__file__), '../output/merged')
out = os.path.join(base, 'logos.hdf5')

img_size = 64

# helper function since we skipped some images
def read_img (fn):
    img = Image.open(fn)
    w, h = img.size
    if w != img_size or h != img_size:
        raise ValueError('Bad size.')

# print out the number of valid versus invalid images
def stats ():
    i = 0
    j = 1
    for img in os.listdir(merged):
        fpath = os.path.join(merged, img)
        try:
            read_img(fpath)
        except: # IOError:
            print 'was not able to read', fpath
            j += 1
            continue

        i += 1

    print '{} valid image, {} invalid'.format(i, j)

# create an CSV file, mapping index to image file name
def save_index ():
    i = 0
    with open('index.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        for img in os.listdir(merged):
            fpath = os.path.join(merged, img)
            try:
                read_img(fpath)
            except:
                continue
            
            writer.writerow([i, img])
            i += 1

# save the i-th image from h5py, for debugging
def visualize (i):
    f = h5py.File(out, 'r')
    dset = f['logos']
    img = Image.fromarray(dset[i], 'RGB')
    img.save('probe{}.png'.format(i))

if __name__ == '__main__':
    # stats()
    save_index()
   
# -*- coding: utf-8 -*-
# recover image file names and meta data from h5 indices

import os
import h5py
import csv
import json
import re
import numpy as np
from PIL import Image

base = '/Users/yliu0/data/'
output = os.path.join(os.path.dirname(__file__), '../output/')
merged = os.path.join(output, 'merged')
h5 = os.path.join(base, 'logos.hdf5')
fn_index = os.path.join(output, 'index.csv')
fn_meta = os.path.join(output, 'meta.csv')
fn_all = os.path.join(output, 'database.csv')

img_size = 64
num_chns = 3

# helper function since we skipped some images
def read_img (fn):
    img = Image.open(fn)
    w, h = img.size
    if w != img_size or h != img_size:
        raise ValueError('Bad size.')

# given an image uint array of shape (w, h, channel)
# return a single hex color
def average_color (arr):
    arr = arr.reshape((img_size * img_size, num_chns))
    avg = np.floor(np.mean(arr, axis = 0))
    # get the hex code
    code = ''
    for index, x in np.ndenumerate(avg):
        c = hex(x)[2:-1] # remove '0x' at the beginning
        c += '0' if len(c) == 1 else '' # if number is single digit, pad with 0
        code += c
    return '#' + code

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
# also augment with average color across all pixels
def save_index ():
    i = 0
    f = h5py.File(h5, 'r')
    dset = f['logos']

    with open(fn_index, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        for img in os.listdir(merged):
            fpath = os.path.join(merged, img)
            try:
                read_img(fpath)
            except:
                continue
            
            color = average_color(dset[i])
            writer.writerow([i, img, color])
            i += 1
    f.close()

# save the i-th image from h5py, for debugging
def visualize (i):
    f = h5py.File(h5, 'r')
    dset = f['logos']
    img = Image.fromarray(dset[i], 'RGB')
    img.save('probe{}.png'.format(i))

    f.close()

def safe_key (arr, key):
    s = arr[key] if key in arr else None
    if isinstance(s, basestring):
        s = s.encode('utf-8')
    return s

# create a CSV file, mapping image file name to other meta data
def save_meta ():
    d = {} # key by image name
    regex = re.compile('\..+')
    count = 0 # number of duplicates

    for f in os.listdir(output):
        _, ext = os.path.splitext(f)
        if ext == '.json':
            print 'Processing {} ...'.format(f)
            with open(os.path.join(output, f)) as jsonfile:
                arr = json.load(jsonfile)
                for item in arr:
                    if len(item['files']) > 0:
                        fn = item['files'][0]['path']
                        if not fn.endswith('.png'):
                            fn = re.sub(regex, '.jpg', fn) # replace weird extension
                        fn = fn.replace('full/', '', 1) # strip off prefix
                        if fn in d:
                            count += 1
                        else:
                            url = safe_key(item, 'website')
                            name = safe_key(item, 'name')
                            industry = safe_key(item, 'industry')
                            country = safe_key(item, 'country')
                            employees = safe_key(item, 'employees')
                            founded = safe_key(item, 'founded')

                            row = [fn, name, url, industry, country, employees, founded, f.replace('.json', '')]
                            d[fn] = row

    with open(fn_meta, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        writer.writerow(['Filename', 'Company Name', 'URL', 'Industry','Country', 'Emloyees', 'Founded', 'Data Source'])
        for key in d:
            writer.writerow(d[key])

    print 'Done: {} duplicates.'.format(count)

# combine the two CSV files by joining image file names
def combine ():
    d = {} # key by image name
    schema = ['Index']
    with open(fn_meta, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        for row in reader:
            if row[0] == 'Filename':
                schema += row + ['Mean Color']
            else:
                d[row[0]] = row

    with open(fn_index, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        with open(fn_all, 'wb') as f:
            writer = csv.writer(f, delimiter = ',')
            writer.writerow(schema)
            for row in reader:
                key = row[1]
                if not key in d:
                    print 'Missing meta: {}'.format(key)
                    continue
                row = row[:1] + d[key] + row[-1:]
                writer.writerow(row)

if __name__ == '__main__':
    # stats()
    # save_index()
    # save_meta()
    combine()

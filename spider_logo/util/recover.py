# -*- coding: utf-8 -*-
# recover image file names and meta data from h5 indices

import os
import h5py
import csv
import json
import re
from PIL import Image

base = '/Users/yliu0/data/'
output = os.path.join(os.path.dirname(__file__), '../output/')
merged = os.path.join(output, 'merged')
h5 = os.path.join(base, 'logos.hdf5')

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
    with open(os.path.join(output, 'index.csv'), 'wb') as csvfile:
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
    f = h5py.File(h5, 'r')
    dset = f['logos']
    img = Image.fromarray(dset[i], 'RGB')
    img.save('probe{}.png'.format(i))

def safe_key (arr, key):
    s = arr[key] if key in arr else None
    if isinstance(s, basestring):
        s = s.encode('utf-8')
    return s

# create a CSV file, mapping image file name to other meta data
def save_meta ():
    d = {} # key by image name
    regex = re.compile('\..+')

    for f in os.listdir(output):
        _, ext = os.path.splitext(f)
        if ext == '.json':
            print 'Processing {} ...'.format(f)
            with open(os.path.join(output, f)) as jsonfile:
                arr = json.load(jsonfile)
                for item in arr:
                    if len(item['files']) > 0:
                        fn = item['files'][0]['path']
                        fn = re.sub(regex, '.jpg', fn) # replace weird extension
                        fn = fn.replace('full/', '', 1) # strip off prefix
                        if fn in d:
                            if d[fn]['name'] != item['name']:
                                print '{} has conflicting names: {}, {}'.format(fn, d[fn]['name'], item['name'])
                        else:
                            url = safe_key(item, 'website')
                            name = safe_key(item, 'name')
                            industry = safe_key(item, 'industry')
                            country = safe_key(item, 'country')
                            employees = safe_key(item, 'employees')
                            founded = safe_key(item, 'founded')

                            # our schema: filename, name, url, industry, country, employees, founded
                            row = [fn, name, url, industry, country, employees, founded]
                            d[name] = row

    with open(os.path.join(output, 'meta.csv'), 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        writer.writerow(['Filename', 'Company Name', 'URL', 'Industry','Country', 'Emloyees', 'Founded'])
        for key in d:
            writer.writerow(d[key])

if __name__ == '__main__':
    stats()
    save_index()
    save_meta()
   
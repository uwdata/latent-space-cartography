# -*- coding: utf-8 -*-

# preprocess emoji images, and output a H5 dataset

import os
import shutil
import h5py
import csv
import numpy as np
from PIL import Image

base = '/Users/yliu0/data/emoji/'
din = base + 'emoji_raw'
dout = base + 'emoji'
h5 = base + 'emoji.h5'
mapping = base + 'emoji_index.csv'

img_size = goal_size = 64
num_chns = 4
valid_exts = ['.png']

def clean (src, dir):
    print 'Duplicating ...'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    shutil.copytree(src, dir)

def center_image (img):
    # calculate size and position
    w, h = img.size
    size = max(w, h)
    out = Image.new('RGBA', (size, size), color = (0, 0, 0, 0))
    upper = ((size - w) / 2, (size - h) / 2)

    # use alpha channel as mask
    out.paste(img, box = upper, mask = img)

    img.close()
    return out

def resize (dir):
    print 'Resizing ...'
    c1 = c2 = c3 = 0

    for f in os.listdir(dir):
        bn, ext = os.path.splitext(f)

        if ext in valid_exts:
            fullpath = os.path.join(dir, f)
            img = Image.open(fullpath)
            w, h = img.size

            # some image has mode P
            img = img.convert('RGBA')

            # ensure all images are square in shape
            if w != h:
                img = center_image(img)
                c1 += 1

            # resize
            if w != goal_size or h != goal_size:
                c2 += 1
                # BICUBIC leads to bleeding, NEAREST leads to aliasing
                # visual quality is also better than resize() with ANTIALIAS
                img.thumbnail((goal_size, goal_size), Image.BILINEAR)

            img.save(fullpath, 'PNG')

            # remove any images that's not our target size
            w, h = img.size
            img.close()
            if w != goal_size or h != goal_size or ext != '.png':
                os.remove(fullpath)
                c3 += 1
        else:
            print ext

    print 'Done: centered {} files, resized {} files, and removed {} files.' \
        .format(c1, c2, c3)

def read_img (fn):
    img = Image.open(fn)
    w, h = img.size
    if w != img_size or h != img_size:
        raise ValueError('Bad size.')

    data = np.asarray(img, dtype=np.uint8)
    chns = data.shape[2]

    if chns != num_chns:
        print fn, data.shape
        raise ValueError('No alpha channel.')

    return data

def gen_data (dir, out, log):
    mp = []

    f = h5py.File(out, 'w')
    dset = f.create_dataset('emoji', (1, img_size, img_size, num_chns), 
            chunks=(1, img_size, img_size, num_chns),
            maxshape=(None, img_size, img_size, num_chns),
            dtype='u1')

    i = 0
    for img in os.listdir(dir):
        fpath = os.path.join(dir, img)
        try:
            data = read_img(fpath)
            mp.append([i, fpath])
        except: # IOError:
            print 'was not able to read', fpath
            continue

        dset.resize((i+1, img_size, img_size, num_chns))
        dset[i] = data
        i += 1
        f.flush()

    f.close()

    with open(log, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        writer.writerow(['i', 'image name'])
        for m in mp:
            writer.writerow(m)

if __name__ == '__main__':
    # clean(din, dout)
    # resize(dout)
    gen_data(dout, h5, mapping)

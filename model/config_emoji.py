#!/usr/bin/env python
# configurations unique to emoji dataset

dset = 'emoji'
img_rows, img_cols, img_chns = 64, 64, 4
img_mode = 'RGBA'
train_split = 19500

fn_raw = 'emoji.h5'
key_raw = 'emoji' # the dataset key in hdf5 file

dims = [4, 8, 16, 32, 64, 128, 256, 512, 1024] # all latent dims

# MySQL table schema
schema_meta = 'i, name, mean_color, category, platform, version, codepoints, shortcode'

#!/usr/bin/env python
# configurations unique to logo dataset

dset = 'logo'
data_type = 'image'
img_rows, img_cols, img_chns = 64, 64, 3
img_mode = 'RGB'
train_split = 15000

fn_raw = 'logos.hdf5'
key_raw = 'logos' # the dataset key in hdf5 file

dims = [32, 64, 128, 256, 512, 1024] # all latent dims

# MySQL table schema
schema_meta = 'i,name,mean_color,data_source,industry'
schema_header = None

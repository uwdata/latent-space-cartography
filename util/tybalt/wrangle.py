# -*- coding: utf-8 -*-

import os
import csv
import h5py
import numpy as np
from shutil import copyfile

base = '/Users/yliu0/code/tybalt/'
p_latent = os.path.join(base, 'data', 'encoded_rnaseq_onehidden_warmup_batchnorm.tsv')
p_raw = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq.h5')
p_id = os.path.join(base, 'data', 'patient_id.csv')
p_clinical = os.path.join(base, 'data', 'tybalt_features_with_clinical.tsv')
p_header = os.path.join(base, 'data', 'pancan_scaled_zeroone_rnaseq_header.csv')

out_base = '/Users/yliu0/data/tybalt/'
out_latent = os.path.join(out_base, 'latent/latent100.h5')
out_raw = os.path.join(out_base, 'raw.h5')
out_db = os.path.join(out_base, 'database.csv')
out_header = os.path.join(out_base, 'header.csv')

# read tsv, discarding (optionally) the first row and (optionally) the first column
def read_tsv (fn, dtype=float, col_start=1, row_start=1):
    res = []
    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            res.append(row[col_start:])
    res = np.asarray(res[row_start:], dtype=dtype)
    return res

# read csv that contain only one row (typically meta data)
def read_csv_single (fn):
    res = []
    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            res = row
    return np.asarray(res)

def convert_ls ():
    res = read_tsv(p_latent)

    f = h5py.File(out_latent, 'w')
    dset = f.create_dataset('latent', data=res)
    f.close()

def copy_raw ():
    copyfile(p_raw, out_raw)

# produce a CSV file of meta data to be imported into database
def wrangle_meta ():
    # read meta data
    res = read_tsv(p_clinical, str, 0)
    n = res.shape[0]
    meta = np.concatenate((res[:, 0].reshape(n, 1), res[:, 101:]), axis=1)

    # read patient ID
    pid = read_csv_single(p_id)

    out = []
    out.append(['i', 'name', 'sample_base', 'platform', 'portion_id',
    'age_at_diagnosis', 'stage', 'vital_status', 'race', 'acronym', 'disease',
    'organ', 'drug', 'ethnicity', 'percent_tumor_nuclei', 'gender', 'sample_type',
    'analysis_center', 'year_of_diagnosis'])
    j = 0
    for i in range(pid.shape[0]):
        row = [''] * n
        row[0] = i
        row[1] = pid[i]
        if pid[i] == meta[j][0]:
            # replace the annoying 'NA' with null value
            for k in range(meta.shape[1]):
                if meta[j][k] == 'NA':
                    meta[j][k] = ''
            # the patient ID matches, so we populate the row
            row[2:] = meta[j][1:]
            j += 1
        out.append(row)

    with open(out_db, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for row in out:
            writer.writerow(row)

# produce a CSV to be imported into database, that contains gene names
def wrangle_header ():
    header = read_csv_single(p_header)
    with open(out_header, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['i', 'name'])
        for i in range(header.shape[0]):
            writer.writerow([i, header[i]])

if __name__ == '__main__':
    # convert_ls()
    # copy_raw()
    # wrangle_meta()
    wrangle_header()

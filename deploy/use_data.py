#!/usr/bin/env python

import os
import argparse
import urllib2
import zipfile
import shutil

urls = {
    'emoji': 'https://onedrive.live.com/download?cid=14E816594A8F732F&resid=14E816594A8F732F%21192&authkey=AKMBM9ZZiKXbucE',
    'tybalt': 'https://onedrive.live.com/download?cid=14E816594A8F732F&resid=14E816594A8F732F%21191&authkey=AB7Q-lSvqBVLjfo',
    'glove_6b': 'https://onedrive.live.com/download?cid=14E816594A8F732F&resid=14E816594A8F732F%21190&authkey=APVJGaWeQehdA34'
}

P_DATA = './data/'
P_CFG = '../model/'
P_UI_CFG = './configs/'

# terminal text colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# connect to SQLite db
def connect_db ():
    import sqlite3
    p_db = P_DATA + 'lsc.db'
    conn = sqlite3.connect(p_db)
    cursor = conn.cursor()
    return conn, cursor

# remove files
def remove_files (fs):
    print 'Deleting files ...'

    for f in fs:
        f = fs[f]
        if os.path.exists(f):
            if os.path.isfile(f):
                os.remove(f)
            else:
                shutil.rmtree(f)
            print f

    print bcolors.OKGREEN + 'Delete files: done.' + bcolors.ENDC

# precompute
def compute (dset):
    print 'Performing precomputation ...\n'
    from precompute import RandomCosine
    from config_data import dims

    rc = RandomCosine(dset, dims)
    rc.compute()

    print bcolors.OKGREEN + '\nPrecompute: success!\n' + bcolors.ENDC

# drop all tables associated with dset
def drop_tables (dset):
    conn, cursor = connect_db()
    print 'SQLite connected, dropping tables ...'

    ts = ['meta', 'group', 'vector']
    for t in ts:
        q = 'DROP TABLE IF EXISTS {}_{};'.format(dset, t)
        print q
        cursor.execute(q)
    conn.commit()
    conn.close()

    print bcolors.OKGREEN + 'Remove database tables: done.' + bcolors.ENDC

# create tables and import meta
# this will drop the original meta table!!
def create_tables (dset, p_meta):
    import csv

    conn, cursor = connect_db()
    print 'SQLite connected, creating tables ...'

    q1 = '''
    CREATE TABLE IF NOT EXISTS `{}_group` (
        `id` integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        `alias` varchar(255) DEFAULT NULL,
        `list` text,
        `creation_time` datetime DEFAULT CURRENT_TIMESTAMP,
        `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP);
    '''.format(dset)
    cursor.execute(q1)
    print q1

    q2 = '''
    CREATE TABLE IF NOT EXISTS `{}_vector` (
        `id` integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        `description` varchar(255) DEFAULT NULL,
        `start` integer DEFAULT NULL,
        `end` integer DEFAULT NULL,
        `creation_time` datetime DEFAULT CURRENT_TIMESTAMP,
        `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP);
    '''.format(dset)
    cursor.execute(q2)
    print q2

    with open(p_meta, 'rb') as f:
        dr = csv.DictReader(f)
        meta = [i for i in dr]

        cols = meta[0].keys()

        # check required fields
        rq = ['i', 'name']
        for col in rq:
            if col not in cols:
                print bcolors.WARNING + \
                    'Error: required field {} not found in meta.csv'.format(col) + \
                    bcolors.ENDC
                exit(0)
            cols.remove(col)

        # drop previous meta table
        q3 = 'DROP TABLE IF EXISTS {}_meta;'.format(dset)
        cursor.execute(q3)
        print q3

        # create table
        q3 = 'CREATE TABLE IF NOT EXISTS `{}_meta` (\n'.format(dset)
        q3 += '\t`i` integer NOT NULL,\n'
        q3 += '\t`name` varchar(255) DEFAULT NULL,\n'
        for col in cols:
            q3 += '\t`{}` varchar(255) DEFAULT NULL,\n'.format(col)
        q3 += '\tPRIMARY KEY (`i`));\n'
        cursor.execute(q3)
        print q3

        # insert data
        to_db = []
        for i in meta:
            row = (i['i'], i['name'])
            for col in cols:
                row += (i[col],)
            to_db.append(row)
        marks = '?,' * (len(cols) + 2)
        s_col = 'i,name,{}'.format(','.join(cols)) if len(cols) else 'i, name'
        q4 = 'INSERT INTO `{}_meta` ({}) VALUES ({});'.format(dset, s_col, marks[:-1])
        print q4

        conn.text_factory = str
        cursor.executemany(q4, to_db)
        conn.commit()
        conn.close()

    print bcolors.OKGREEN + '\nImport into database: success!\n' + bcolors.ENDC

# download and unzip data
def download (dset):
    # check if we have already an existing directory
    pout = os.path.join(P_DATA, dset)
    if os.path.exists(pout):
        print '{} already exists. Do you want to overwrite?'.format(dset)
        s = raw_input('(y/n): ')
        if s.startswith('y'):
            shutil.rmtree(pout)
        else:
            exit(0)
    os.makedirs(pout)

    fn = '{}_data_temp.zip'.format(dset) # temporary zip file
    u = urllib2.urlopen(urls[dset])
    f = open(fn, 'wb')
    meta = u.info()
    fsize = int(meta.getheaders("Content-Length")[0])
    print 'Downloading ...'

    # display progress
    block = 8192
    total = 0
    while True:
        buffer = u.read(block)
        if not buffer:
            break

        total += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (total, total * 100. / fsize)
        status = status + chr(8) * (len(status) + 1)
        print status,

    f.close()

    # unzip
    zip_ref = zipfile.ZipFile(fn, 'r')
    zip_ref.extractall(pout)
    zip_ref.close()

    # remove the zip file
    os.remove(fn)

# check if the dataset can be downloaded
def check_download (dset):
    if dset not in urls:
        print 'Only the following datasets are available for download:'
        for key in urls:
            print key
        exit(1)

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description='Decide which dataset to work with.')
    parser.add_argument('name', type=str,
        help='name of the dataset')
    parser.add_argument('--download', action='store_true',
        help='download a demo dataset from the web')
    parser.add_argument('--add', action='store_true',
        help='onboard a new, custom dataset')
    parser.add_argument('--remove', action='store_true',
        help='delete data associated with this dataset')

    args = parser.parse_args()
    dset = args.name

    if args.download:
        check_download(dset)

    # required files
    REQ_FS = {
        'config': os.path.join(P_CFG, 'config_{}.py'.format(dset)),
        'json': os.path.join(P_UI_CFG, 'config_{}.json'.format(dset)),
        'data': os.path.join(P_DATA, dset)
    }

    # delete!!
    if args.remove:
        print 'Do you want to permenantly delete all data associated with {}?'.format(dset)
        print 'Type CONFIRM to confirm:'
        s = raw_input('> ')

        if s.startswith('CONFIRM'):
            drop_tables(dset)
            remove_files(REQ_FS)

        exit(0)

    # create data root folder
    if not os.path.exists(P_DATA):
        os.makedirs(P_DATA)

    # verify we have data and configs
    for i in REQ_FS:
        f = REQ_FS[i]
        if i == 'data' and args.download:
            continue # skip
        if not os.path.exists(f):
            if i == 'json':
                # copy default client config
                shutil.copyfile(P_UI_CFG + 'config_default.json', f)
                print bcolors.WARNING + 'Client config not found'
                print 'Creating a default config in {}'.format(f) + bcolors.ENDC
            else:
                print bcolors.WARNING + \
                    'Error: required file not found\n  {}'.format(f) + bcolors.ENDC
                exit(1)

    # copy config
    cfg = './config_data.py'
    shutil.copyfile(REQ_FS['config'], cfg)

    # create database tables
    if args.add:
        # check meta csv
        p_meta = os.path.join(REQ_FS['data'], 'meta.csv')
        if not os.path.exists(p_meta):
            print bcolors.WARNING + \
                'Error: metadata file not found\n  {}'.format(p_meta) + \
                bcolors.ENDC
            exit(1)

        # create database tables
        create_tables(dset, p_meta)

        # precompute pairs.h5
        compute(dset)

    # download the zip file from links
    if args.download:
        download(dset)

    # hint
    print bcolors.OKBLUE + 'Dataset "{}" is ready\n'.format(dset) + bcolors.ENDC
    print 'Next: start the server via\n  python server.py' 

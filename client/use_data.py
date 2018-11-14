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

def connect_db ():
    import sqlite3
    p_db = P_DATA + 'lsc.db'
    conn = sqlite3.connect(p_db)
    cursor = conn.cursor()
    return conn, cursor

def drop_tables (dset):
    conn, cursor = connect_db()
    ts = ['meta', 'group', 'vector']
    for t in ts:
        q = 'DROP TABLE IF EXISTS {}_{};'.format(dset, t)
        print q
        cursor.execute(q)
    conn.commit()
    conn.close()

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
                print 'Error: required field {} not found in meta.csv'.format(col)
                exit(0)
            cols.remove(col)

        # create table
        created = True
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

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description='Decide which dataset to work with.')
    parser.add_argument('name', type=str,
        help='name of the dataset')
    parser.add_argument('--download', action='store_true',
        help='download a demo dataset from the web')
    parser.add_argument('--new', action='store_true',
        help='onboard a new, custom dataset')
    parser.add_argument('--remove', action='store_true',
        help='delete data associated with this dataset')

    args = parser.parse_args()
    dset = args.name

    # delete!!
    if args.remove:
        print 'Do you want to permenantly delete all data associated with {}?'.format(dset)
        print 'Type CONFIRM to confirm:'
        s = raw_input('> ')

        if s.startswith('CONFIRM'):
            drop_tables(dset)

        exit(0)

    # create data root folder
    if not os.path.exists(P_DATA):
        os.makedirs(P_DATA)

    # verify we have data and configs
    p_data = os.path.join(P_DATA, dset)
    if not os.path.exists(p_data) and not args.download:
        print 'Error: data folder not found\n  {}'.format(p_data)
        exit(0)
    cfgs = [
        os.path.join(P_CFG, 'config_{}.py'.format(dset)),
        os.path.join(P_UI_CFG, 'config_{}.json'.format(dset))
    ]
    for pp in cfgs:
        if not os.path.exists(pp):
            print 'Error: config file not found\n  {}'.format(pp)
            exit(0)

    # copy config
    cfg = './config_data.py'
    shutil.copyfile(cfgs[0], cfg)

    # create database tables
    if args.new:
        # check meta csv
        p_meta = os.path.join(p_data, 'meta.csv')
        if not os.path.exists(p_meta):
            print 'Error: metadata file not found\n  {}'.format(p_meta)
            exit(0)

        # create database tables
        create_tables(dset, p_meta)

    # download the zip file from links
    if args.download:
        # check url
        if dset not in urls:
            print 'Only the following datasets are available for download:'
            for key in urls:
                print key
            exit(0)

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

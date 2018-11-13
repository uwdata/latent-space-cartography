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

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description='Decide which dataset to work with.')
    parser.add_argument('name', type=str,
        help='name of the dataset')
    parser.add_argument('--download', action='store_true',
        help='download a demo dataset from the web')

    args = parser.parse_args()
    dset = args.name

    # verify we have data and configs
    if not os.path.exists(P_DATA):
        os.makedirs(P_DATA)
    p_cfg = os.path.join(P_CFG, 'config_{}.py'.format(dset))
    if not os.path.exists(p_cfg):
        print 'Error: config file not found'
        print '  {}'.format(p_cfg)
        exit(0)

    # copy config
    cfg = './config_data.py'
    shutil.copyfile(p_cfg, cfg)

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

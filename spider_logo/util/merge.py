# -*- coding: utf-8 -*-

import os
import shutil
import re

dout = 'merged'
base = os.path.join(os.path.dirname(__file__), '../output/')

def copy_files (src, dst):
    for f in os.listdir(src):
        shutil.copy2(os.path.join(src, f), dst)

def copy (base, dout):
    for name in os.listdir(base):
        path = os.path.join(base, name)
        if os.path.isdir(path) and name != dout:
            print 'Copying {} ...'.format(name)
            copy_files(path, os.path.join(base, dout))

    print 'Done.'

def rename (dir):
    print 'Renaming ...'

    regex = re.compile('\..+')
    for f in os.listdir(dir):
        bn, ext = os.path.splitext(f)
        if not f.startswith('.') and ext != '.png' and ext != '.jpg':
            fnew = re.sub(regex, '.jpg', f)
            os.rename(os.path.join(dir, f), os.path.join(dir, fnew))
    print 'Done.'

if __name__ == '__main__':
    # copy(base, dout)
    # rename(os.path.join(base, dout))
    pass

# -*- coding: utf-8 -*-

import os
import shutil
import re
from PIL import Image

dout = 'merged'
base = os.path.join(os.path.dirname(__file__), '../output/')
valid_exts = ['.png', '.jpg']  # valid image extensions
goal_size = 64

def copy_files (src, dst):
    count = 0
    for f in os.listdir(src):
        shutil.copy2(os.path.join(src, f), dst)
        count += 1

    return count

def center_image (img):
    # handle transparency
    img = img.convert('RGBA')

    # calculate size and position
    w, h = img.size
    size = max(w, h)
    out = Image.new('RGB', (size, size), color = (255, 255, 255))
    upper = ((size - w) / 2, (size - h) / 2)

    # use alpha channel as mask
    out.paste(img, box = upper, mask = img)

    img.close()
    return out

def clean (dir):
    print 'Cleaning leftovers ...'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def copy (base, dout):
    count = 0
    for name in os.listdir(base):
        path = os.path.join(base, name)
        if os.path.isdir(path) and name != dout:
            print 'Copying {} ...'.format(name)
            count += copy_files(path, os.path.join(base, dout))

    print 'Done: copied {} files.'.format(count)

def rename (dir):
    print 'Renaming ...'

    regex = re.compile('\..+')
    count = 0
    for f in os.listdir(dir):
        bn, ext = os.path.splitext(f)
        if not f.startswith('.') and ext not in valid_exts:
            fnew = re.sub(regex, '.jpg', f)
            os.rename(os.path.join(dir, f), os.path.join(dir, fnew))
            count += 1
    print 'Done: renamed {} files.'.format(count)

def resize (dir):
    print 'Resizing ...'
    c1 = c2 = c3 = 0

    for f in os.listdir(dir):
        bn, ext = os.path.splitext(f)

        if ext in valid_exts:
            fullpath = os.path.join(dir, f)
            img = Image.open(fullpath)
            w, h = img.size

            # ensure all images are square in shape
            if w != h:
                img = center_image(img)
                c1 += 1

            # resize
            if w != goal_size or h != goal_size:
                c2 += 1
                img = img.convert('RGB')
                # BICUBIC leads to bleeding, NEAREST leads to aliasing
                # visual quality is also better than resize() with ANTIALIAS
                img.thumbnail((goal_size, goal_size), Image.BILINEAR)
                img.save(re.sub('.png', '.jpg', fullpath), 'JPEG')

            # remove any images that's not our target size
            w, h = img.size
            img.close()
            if w != goal_size or h != goal_size or ext == '.png':
                os.remove(fullpath)
                c3 += 1

    print 'Done: centered {} files, resized {} files, and removed {} files.' \
        .format(c1, c2, c3)

if __name__ == '__main__':
    dir = os.path.join(base, dout)
    clean(dir)
    copy(base, dout)
    rename(dir)
    resize(os.path.join(base, dout))
    pass

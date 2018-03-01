import h5py
from PIL import Image
import os
import numpy as np

base = os.path.join(os.path.dirname(__file__), '../output/')
dir_in = os.path.join(base, 'merged')
out = os.path.join(base, 'logos.hdf5')

num_chns = 3
img_size = 64

def read_img (fn):
    img = Image.open(fn)
    w, h = img.size
    if w != img_size or h != img_size:
        raise ValueError('Bad size.')

    data = np.asarray(img, dtype=np.uint8)
    data = data[:, :, :num_chns] # discard alpha channel if any

    return data

if __name__ == '__main__':
    # clean
    if os.path.exists(out):
        os.remove(out)

    f = h5py.File(out, 'w')
    dset = f.create_dataset('logos', (1, img_size, img_size, num_chns), 
            chunks=(1, img_size, img_size, num_chns),
            maxshape=(None, img_size, img_size, num_chns),
            dtype='u1')

    i = 0
    for img in os.listdir(dir_in):
        fpath = os.path.join(dir_in, img)
        try:
            data = read_img(fpath)
        except: # IOError:
            print 'was not able to read', fpath
            continue

        dset.resize((i+1, img_size, img_size, num_chns))
        dset[i] = data
        i += 1
        f.flush()

    f.close()

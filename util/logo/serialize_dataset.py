import h5py
import os
import numpy as np

dim = 12288

base = '/home/yliu0/data/'
pin= os.path.join(base, 'logos.hdf5')
out = os.path.join(base, './latent/latent{}.h5'.format(dim))

num_chns = 3
img_size = 64

if __name__ == '__main__':
    # clean
    if os.path.exists(out):
        os.remove(out)

    fin = h5py.File(pin, 'r')
    din = fin['logos']

    f = h5py.File(out, 'w')
    dset = f.create_dataset('latent', (1, dim), 
            chunks=(1, dim),
            maxshape=(None, dim),
            dtype='u1')

    l = din.shape[0]
    din = np.reshape(din, (l, dim))
    print din.shape
    for i, val in enumerate(din):
        dset.resize((i + 1, dim))
        dset[i] = val
        f.flush()
    
    f.close()
    fin.close()

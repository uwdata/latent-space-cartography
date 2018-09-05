# -*- coding: utf-8 -*-

import os
import sys
import logging
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec

base = '/Users/yliu0/data/word/'
dims = [50, 100, 200, 300]

def analogy_w2v ():
    fn = './dim300.bin.gz'
    wv = KeyedVectors.load_word2vec_format(fn, binary=True)
    analogy_scores = wv.accuracy('./questions-words.txt')

def convert_glove ():
    for dim in dims:
        fn = base + 'raw/glove.6B/glove.6B.{}d.txt'.format(dim)
        pout = base + 'raw/glove_6b_w2v/glove.6B.{}d.w2v.txt'.format(dim)
        glove2word2vec(fn, pout)

def analogy_glove ():
    test = base + 'benchmarks/questions-words.txt'
    for dim in dims:
        fn = base + 'raw/glove_6b_w2v/glove.6B.{}d.w2v.txt'.format(dim)
        wv = KeyedVectors.load_word2vec_format(fn)
        analogy_scores = wv.accuracy(test, restrict_vocab=10000)

if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)

    # analogy_w2v()
    # convert_glove()
    analogy_glove()

# -*- coding: utf-8 -*-

import os
import sys
import logging
from gensim.models import KeyedVectors

if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)

    fn = './dim300.bin.gz'
    wv = KeyedVectors.load_word2vec_format(fn, binary=True)
    analogy_scores = wv.accuracy('./questions-words.txt')

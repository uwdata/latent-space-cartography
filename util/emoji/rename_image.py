# -*- coding: utf-8 -*-

import os
import csv

base = '/Users/yliu0/data/emoji/'
mapping = base + 'emoji_index.csv'
din = base + 'images/'

with open(mapping, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        # skip header
        if row[0] == 'i':
            continue

        img = os.path.split(row[1])[1]
        print din+img
        os.rename(din + img, '{}{}.png'.format(din, row[0]))

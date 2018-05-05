# -*- coding: utf-8 -*-

import csv

# file paths
fin = 'raw/Company-Categorization-DFE.csv'
fout = 'company-categorization.csv'
fpre = './spider_logo/input/'

# open CSV file to read, then write to a new file
csvin = open(fpre + fin, 'rU')
csvout = open(fpre + fout, 'wb')

reader = csv.reader(csvin, delimiter=',')
writer = csv.writer(csvout, delimiter=',')

# process every row
for row in reader:
    # keep only relevant columns
    writer.writerow([row[20], row[22], row[6], row[18]])

# close file descriptors
csvin.close()
csvout.close()

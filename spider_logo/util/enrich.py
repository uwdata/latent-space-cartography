# -*- coding: utf-8 -*-
# Usage:
# python ./spider_logo/util/enrich.py >> temp.txt

import requests
import csv
import re
import time
import json

# clearbit API
endpoint = 'https://company.clearbit.com/v1/domains/find?name='
headers = {"Authorization":"Bearer sk_dedd790535b6170629589cf4dbcb76e9"}

# file paths
fin = 'forbesglobal2000-2016.csv'
fout = 'forbesglobal2000-2016-clean.csv'
fpre = './spider_logo/input/'

# open CSV file to read, then write to a new file
csvin = open(fpre + fin, 'rb')
csvout = open(fpre + fout, 'wb')

reader = csv.reader(csvin, delimiter=',')
writer = csv.writer(csvout, delimiter=',')

# process every row
for row in reader:
    # header row
    if row[0] == '_ - uri':
        writer.writerow(['domain'] + row)
    else:
        # remove the "Group" word in company name
        name = re.sub(' Group', '', row[2])

        # query clearbit API to get company domain
        res = requests.get(endpoint + name, headers = headers)
        data = res.json()
        if 'error' not in data:
            print json.dumps(data, indent = 4, sort_keys = True)
        domain = data['domain'] if 'domain' in data else ''
        writer.writerow([domain] + row)

        # limit to 600 requests per minute
        time.sleep(0.1)

# close file descriptors
csvin.close()
csvout.close()

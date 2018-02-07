# -*- coding: utf-8 -*-

from spider_logo.items import Logo
import datetime
import scrapy
import csv

# To run the spider, in the project root directory:
# scrapy crawl spider-forbes -o forbes2000.json

class LogoSpider(scrapy.Spider):
    name = 'spider-forbes'

    # let's have a fake start url ...
    start_urls = ['https://scrapy.org/']

    def parse(self, response):
        # read our list of companies from a file
        f = open('./spider_logo/input/forbesglobal2000-2016-clean.csv', 'rb')
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            # skip header
            if row[0] == 'domain':
                continue

            name = row[3]
            country = row[4]
            industry = row[10]
            url = row[0]
            img = 'https://logo.clearbit.com/' + url + '?s=512'

            yield Logo(name = name, website = url, file_urls = [img],\
                country = country, industry = industry)

        f.close()

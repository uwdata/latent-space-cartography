# -*- coding: utf-8 -*-

from spider_logo.items import Logo
import datetime
import scrapy
import csv
import re

# To run the spider, in the project root directory:
# scrapy crawl spider-martech -o martech5000.json

class LogoSpider(scrapy.Spider):
    name = 'spider-martech'

    # let's have a fake start url ...
    start_urls = ['https://scrapy.org/']

    def parse(self, response):
        # read our list of companies from a file
        f = open('./spider_logo/input/martech2017.csv', 'rb')
        reader = csv.reader(f, delimiter=',')

        # crawl each row
        for row in reader:
            url = row[3]
            img = 'https://logo.clearbit.com/' + url + '?s=512'
            yield Logo(name = row[2], website = url, file_urls = [img],\
                industry = 'Marketing Technology:' + row[1])
        f.close()

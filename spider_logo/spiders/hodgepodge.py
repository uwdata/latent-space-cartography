# -*- coding: utf-8 -*-

from spider_logo.items import Logo
import datetime
import scrapy
import csv
import re

# To run the spider, in the project root directory:
# scrapy crawl spider-hp -o hodgepodge.json

class LogoSpider(scrapy.Spider):
    name = 'spider-hp'

    # let's have a fake start url ...
    start_urls = ['https://scrapy.org/']

    def parse(self, response):
        # read our list of companies from a file
        f = open('./spider_logo/input/company-categorization.csv', 'rU')
        reader = csv.reader(f, delimiter=',')

        # regex to remove the https:// or http:// prefix of urls
        regex = re.compile('^[a-z]+:\/\/')
        # regex to remove anything after the first /
        regex2 = re.compile('\/.*$')

        # crawl each row
        for row in reader:
            url = re.sub(regex2, '', re.sub(regex, '', row[1]))
            img = 'https://logo.clearbit.com/' + url + '?s=512'
            yield Logo(name = row[0], website = url, file_urls = [img],\
                country = row[3], industry = row[2])
        f.close()

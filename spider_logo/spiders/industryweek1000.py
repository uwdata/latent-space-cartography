# -*- coding: utf-8 -*-

from spider_logo.items import Logo
import datetime
import scrapy
import csv

# To run the spider, in the project root directory:
# scrapy crawl spider-iw -o iw1000.json

class LogoSpider(scrapy.Spider):
    name = 'spider-iw'

    # let's have a fake start url ...
    start_urls = ['https://scrapy.org/']

    def parse(self, response):
        # read our list of companies from a file
        f = open('./spider_logo/input/IndustryWeek1000.csv', 'rb')
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            # skip header
            if row[0] == 'Id':
                continue

            name = row[1]
            industry = row[2]
            country = row[3]
            url = row[4]
            img = 'https://logo.clearbit.com/' + url + '?s=512'

            yield Logo(name = name, website = url, file_urls = [img],\
                country = country, industry = industry)

        f.close()

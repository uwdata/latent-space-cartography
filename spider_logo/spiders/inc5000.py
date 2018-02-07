# -*- coding: utf-8 -*-

from spider_logo.items import Logo
import datetime
import scrapy
import json
import re

# To run the spider, in the project root directory:
# scrapy crawl spider-i5 -o inc5000.json

class LogoSpider(scrapy.Spider):
    name = 'spider-i5'

    # let's have a fake start url ...
    start_urls = ['https://scrapy.org/']

    def parse(self, response):
        # read our list of companies from a file
        f = open('./spider_logo/input/Inc5000_2017_JSON.txt')
        data = json.load(f)['sites']
        f.close()

        # regex to remove the https:// or http:// prefix of urls
        regex = re.compile('^[a-z]+:\/\/')

        for site in data:
            name = site['company']
            url = re.sub(regex, '', site['website'])
            img = 'https://logo.clearbit.com/' + url + '?s=512'
            yield Logo(name = name, website = url, file_urls = [img])

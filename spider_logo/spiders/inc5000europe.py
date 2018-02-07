# -*- coding: utf-8 -*-

from spider_logo.items import Logo
import datetime
import scrapy
import csv
import re

# To run the spider, in the project root directory:
# scrapy crawl spider-i5-europe -o inc5000europe.json

class LogoSpider(scrapy.Spider):
    name = 'spider-i5-europe'
    rotate_user_agent = True

    # let's have a fake start url ...
    start_urls = ['https://www.inc.com/']

    def parse(self, response):
        # read our list of companies from a file
        with open('./spider_logo/input/inc5000europe.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                # skip header
                if row[0] == 'url':
                    continue

                # follow the profile link
                link = re.sub('^http', 'https', row[0])
                req = scrapy.Request(link, self.parse_page)

                # pass these attributes to the callback
                req.meta['name'] = row[4]
                req.meta['country'] = row[6]
                req.meta['industry'] = row[7]
                yield req
    
    # parse the profile page to get the company url
    def parse_page(self, response):
        # these attributes comes from the csv file
        name = response.meta['name']
        country = response.meta['country']
        industry = response.meta['industry']

        # extract url from the webpage, removing any http:// or https:// prefix
        url = response.css('dd.website a::attr(href)').extract_first()
        url = re.sub('^[a-z]+:\/\/', '', url)

        # extract other fields
        founded = response.css('dl.ifc_founded dd::text').extract_first()
        employees = response.css('dl.employees dd::text').extract_first()

        # store data
        img = 'https://logo.clearbit.com/' + url + '?s=512'
        yield Logo(name = name, website = url, file_urls = [img],\
            country = country, industry = industry, founded = founded,\
            employees = employees)

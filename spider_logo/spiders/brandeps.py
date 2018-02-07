# -*- coding: utf-8 -*-

from spider_logo.items import Logo
import datetime
import scrapy
import re

# To run the spider, in the project root directory:
# scrapy crawl spider-brandeps -o brandeps.json

page = 1

class LogoSpider(scrapy.Spider):
    name = 'spider-brandeps'
    rotate_user_agent = True

    start_urls = ['https://www.brandeps.com/logo/Latest']

    def parse(self, response):
        # scrape all logo images
        for div in response.css('div.resultsgroup'):
            img = div.css('a img::attr(src)').extract_first()
            alt = div.css('a img::attr(alt)').extract_first()
            name = re.sub(' logo vector', '', alt)
            yield Logo(name = name, website = '', file_urls = [img])
        
        # next page
        global page
        page += 1
        if page <= 50:
            prefix = 'https://www.brandeps.com/logo/Latest?order=&page='
            yield scrapy.Request('{}{}'.format(prefix, page), self.parse)

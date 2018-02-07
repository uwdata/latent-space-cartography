# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Logo(scrapy.Item):
    name = scrapy.Field()       # company name
    website = scrapy.Field()    # company website
    file_urls = scrapy.Field()  # built-in name for scraping binary data
    files = scrapy.Field()      # built-in name for scraping binary data

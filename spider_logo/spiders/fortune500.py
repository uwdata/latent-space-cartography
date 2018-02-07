# -*- coding: utf-8 -*-

from spider_logo.items import Logo
import datetime
import scrapy

# To run the spider:
# scrapy crawl spider-fortune500 -o fortune500.json

class LogoSpider(scrapy.Spider):
	name = 'spider-fortune500'
	start_urls = ['https://www.zyxware.com/articles/4344/list-of-fortune-500-companies-and-their-websites']

	def parse(self, response):
		for item in response.css('tbody tr'):
			url = item.css('td a::text').extract_first()
			name = item.css('td::text')[1].extract()
			img = 'https://logo.clearbit.com/' + url + '?s=512'
			yield Logo(name = name, website = url, file_urls = [img])

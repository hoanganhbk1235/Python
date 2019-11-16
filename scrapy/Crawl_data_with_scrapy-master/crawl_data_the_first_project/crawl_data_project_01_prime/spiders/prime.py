# task: from web: prime.vn
# take the every infor of products

# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
import pdb

class Prime02Spider(scrapy.Spider):
    name = 'prime02'
    allowed_domains = ['prime.vn']
    def start_requests(self):
    	urls = [
    	'https://www.prime.vn/san-pham/gach-ceramic',
    	]
    	for url in urls:
    		yield scrapy.Request(url = url, callback = self.parse)

    # function "parse" make the Resquest to take the info of all products in current page
    def parse(self, response):
        #inspect_response(response, self)
        
        # using xpath to access the containing cards of all products in this page
        products = response.xpath('//div[@class = "product"]')

        for product in products:
            # take the link to each product
            link_of_product = product.xpath('.//div[@class = "product__info"]//a[@target = "_blank"]/@href').extract_first()

            #pdb.set_trace()
            # make the Request to take the info of each product
            yield scrapy.Request(url = link_of_product, callback = self.parse_item)

            #pdb.set_trace()
        # take the link of next page
        arrow = response.xpath('//span[@class = "arrow_carrot-right"]')
        # the way 1:
        #next_page = arrow.xpath('../@href').extract_first()

        # the way 2
        next_page = arrow.xpath('parent::*/@href').extract_first()
        #pdb.set_trace()
        # then next page was found, we need check. 
        # If netx_page not empty, we need make the Request to take infor of all product in this page
        if next_page:
            yield scrapy.Request(url = next_page, callback = self.parse)


    # function "parse_item" make the Resquest to take the all info of each product
    def parse_item(self, response):
        #inspect_response(response, self)
        # create a new dictionary variable, item, contain the indo of product
        item = dict()

        prod = response.xpath('//div[@class = "container wrap-product-detail"]')
        prod_img = prod.xpath('.//div[@class = "slider-album"]')
        prod_content = prod.xpath('.//div[@class = "product__content-wrapper"]')

        # take code of product
        item['code'] = prod_content.xpath('.//div[@class = "product-code-name"]/text()').extract_first()
        # take img of product
        item['image'] = prod_img.xpath('.//figure/img/@src').extract_first()
        # take key of product info 
        item_key = prod_content.xpath('.//ul[@class = "product__list--attr"]//p[@class = "product__list--attr-name"]/text()').extract()
        # take value correspond with key of product info
        item_value = prod_content.xpath('.//ul[@class = "product__list--attr"]//p[@class = "product__list--attr-info"]/a/text()').extract()

        item.update(dict(zip(item_key, item_value)))
        return item



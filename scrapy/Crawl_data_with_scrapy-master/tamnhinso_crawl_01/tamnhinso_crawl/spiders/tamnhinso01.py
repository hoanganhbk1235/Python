# -*- coding: utf-8 -*-
import scrapy
import pdb
from scrapy.shell import inspect_response
from scrapy.linkextractors import LinkExtractor


class Tamnhinso01Spider(scrapy.Spider):
	name = 'tamnhinso01'
	allowed_domains = ['tamnhinso.info']
	def start_requests(self):
		urls = [
		'http://tamnhinso.info/phim/phim-le/viewbycategory'
		]
		for url in urls:
			yield scrapy.Request(url = url, callback = self.parse)

	def parse(self, response):
		#inspect_response(response, self)
		products = LinkExtractor(restrict_xpaths = './/div[@class = "col-md-2 col-xs-6 movie-item"]//a[@class = "Tooltip"]').extract_links(response)
		#pdb.set_trace()

		for product in products:
			link_prod = product.url
			#pdb.set_trace()

			yield scrapy.Request(url = link_prod, callback = self.parse_item)

		# debug pages : stoping in a page 2 test with scrapy.shell
		# create a new variable, page, contain the index of pages
		# if we are page_1 return None , if page_2 will stop and check
		#page =  1 if response.meta.get('page') is None else response.meta.get('page')
		#                       if page == 2:
		#                          inspect_response(response, self)

		# find all the a[@class = "text"] cards is the son card of the nav card                           
		link_of_pages = response.xpath('//div[@class="section sectionMain movie-tns"]//nav//a[@class="text"]')
		# we is taked 2 links of page with ( text = "< Quay lai" ) and (text = "Tiep theo >")

		# check the every page links
		for i in link_of_pages:
			#print(i)
			# we find the link of page contain text = "Tiep theo >"
			if i.xpath('./text()').extract_first() == 'Tiếp theo >':
				# then take (@href) field of next page
				n_page = i.xpath('./@href').extract_first()
				# result : phim/phim-le/viewbycategory?page=2, 3, ...




		# we need add domain for the link of page
		next_page = response.follow(n_page).url
		# resuslt : http://tamnhinso.info/phim/phim-le/viewbycategory?page=2, 3, ...
		#pdb.set_trace()


		# make Request for the next page
		if next_page:
			yield scrapy.Request(url = next_page, callback = self.parse)


	def parse_item(self, response):

		#inspect_response(response, self)
		item = dict()

		prod = response.xpath('.//div[@class = "movie-detail"]')
		#pro_info = prod.xpath('.//div[@class= "cf pt-30 row"]')

		# take image
		item['image'] = prod.xpath('.//img[@itemprop = "image"]/@src').extract_first()

		# take movie name and genre
		prod_name = prod.xpath('.//div[@class = "col-md-9"]')
		# movie name
		item['item_en'] = prod_name.xpath('.//h1[@class = "movie-title-en"]/text()').extract_first()
		item['item_vi'] = prod_name.xpath('.//h2[@class = "movie-title-vi"]/text()').extract_first()
		# movie genre
		genre_key = prod_name.xpath('.//p[@class = "genre"]/@class').extract()
		genre_value = prod_name.xpath('.//p[@class = "genre"]/a/text()').extract()
		# convert list to string
		genre_value_str = '/'.join(genre_value)
		# convert str to list
		genre_value_list = []
		genre_value_list.append(genre_value_str)
		# key and value the same type (list)
		item.update(dict(zip(genre_key,genre_value_list)))
		#pdb.set_trace()

		# take the download link of movie

		# take describe and infor of movie 
		item['describe'] = prod.xpath('.//div[@itemprop= "description"]/text()').extract_first()
		#prod_info = prod.xpath('.//div[@class = "cf pt-30 row"]//div[@class= "col-md-6 "]')

		# the way 1
		# take infor of movie

		prod_info = prod.xpath('.//div[@class= "cf pt-30 row"]//div[@class = "col-md-6 "]')
		# in the movie infor contain 6 the tr card , we will take the infor of the each card

		# tr[1]
		# take text of the tr[1]/td[1] card that contain field name : "Quoc Gia"
		key_tr_1 = prod_info.xpath('.//table//tr[1]/td[1]/text()').extract_first()
		# take text of the tr[1]/td[1]/a[@class ='...'] card that contain the infor of field name : "ten quoc gia"
		item[key_tr_1] = prod_info.xpath('.//table//tr[1]/td[2]/a[@class = "Tooltip"]/text()').extract_first()
		
		# tr[2]
		key_tr_2 = prod_info.xpath('.//table//tr[2]/td[1]/text()').extract_first()
		item[key_tr_2] = prod_info.xpath('.//table//tr[2]/td[2]/div/text()').extract_first()

		# tr[3]
		key_tr_3 = prod_info.xpath('.//table//tr[3]/td[1]/text()').extract_first()
		item[key_tr_3] = prod_info.xpath('.//table//tr[3]/td[2]/div/text()').extract_first()

		# tr[4]
		key_tr_4 = prod_info.xpath('.//table//tr[4]/td[1]/text()').extract_first()
		item[key_tr_4] = prod_info.xpath('.//table//tr[4]/td[2]/div/span/a/text()').extract_first()

		# tr[5]
		key_tr_5 = prod_info.xpath('.//table//tr[5]/td[1]/text()').extract_first()
		item[key_tr_5] = prod_info.xpath('.//table/tr[5]/td[2]/text()').extract_first()

		# tr[6] : part 1 : take the number star of movie
		key_tr_6 = prod_info.xpath('.//table//tr[6]/td[1]/text()').extract_first()
		item[key_tr_6] = prod_info.xpath('.//table//tr[6]/td[2]/label/div/@data-score').extract_first()
		# tr[6]: part 2 : taking the number was rated for movie
		a = prod_info.xpath('.//table//tr[6]//td[1]/span/text()').extract_first()
		if a is None:
			item['rate_number'] = 0
		else:
			item['rate_number'] = a


		#pdb.set_trace()
		return item
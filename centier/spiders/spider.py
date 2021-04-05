import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CcentierItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CcentierSpider(scrapy.Spider):
	name = 'centier'
	start_urls = ['https://www.centier.com/news/']

	def parse(self, response):
		post_links = response.xpath('//span[@class="title"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="pagesLinks next-link"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//p[@class="date highlight"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="content-wrapper"]//text()[not (ancestor::div[@class="blog-categories"] or ancestor::div[@class="article-nav"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CcentierItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

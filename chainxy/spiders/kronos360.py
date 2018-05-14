import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree
import time
import pdb

class Kronos360Spider(scrapy.Spider):
    name = "kronos360"

    request_url = "https://www.kronos360.com/en/luxury-watches/?p=##page##"
    storeNumbers = []
    pages = 7
    base_url = "http://www.filipucci.nl/en/"

    def start_requests(self):
        for index in range(0, self.pages):
            yield scrapy.Request(url=self.request_url.replace('##page##', str(index)))

    def parse(self, response):
        items = response.xpath('//div[@class="item product-ctn cols animated-full lg4 sm4 xs6 col-xxs-6"]')
        for item in items:
            price = item.xpath('.//span[@itemprop="price"]/@content').extract_first()
            if int(price) < 1000:
                continue

            url = item.xpath('.//a[@class="product-img"]/@href').extract_first()
            yield scrapy.Request(url=url, callback=self.parse_watch)

    def parse_watch(self, response):
        item = ChainItem()
        
        try:
            item['website_id'] = response.xpath('//input[@name="id_product"]/@value').extract_first()
            item['watchr_id'] = "empty"
            item['shop_id'] = "Shop8"
            item['sku'] = "empty"
            item['price'] = response.xpath('//span[@itemprop="price"]/@content').extract_first()

            item['watchr_price'] = ''
            item['currency'] = response.xpath('//meta[@itemprop="priceCurrency"]/@content').extract_first()

            item['dealer_link'] = response.url
            image_urls = response.xpath('//ul[@id="thumbs_list_frame"]/li/@data-src').extract()

            item['img_link'] = "" + ', '.join(image_urls) + ""

            item['description'] = response.xpath('//meta[@property="og:description"]/@content').extract_first()
            item['exp_description'] = ''
            item['gemstones'] = ''
            
            tr_list = response.xpath('//div[@id="features"]//li')
            # pdb.set_trace()
            for tr in tr_list:
                try:
                    if "Year" in tr.xpath('./span/text()').extract_first():
                        item['year'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Brand" in tr.xpath('./span/text()').extract_first():
                        item['brand'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Model" in tr.xpath('./span/text()').extract_first():
                        item['model'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue

                try:
                    if "Box" in tr.xpath('./span/text()').extract_first():
                        item['box'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue

                try:
                    if "Reference" in tr.xpath('./span/text()').extract_first():
                        item['ref'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Size" in tr.xpath('./span/text()').extract_first():
                        item['case_size'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Glass" in tr.xpath('./span/text()').extract_first():
                        item['crystal'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Dial" in tr.xpath('./span/text()').extract_first():
                        item['dial_color'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Movement" in tr.xpath('./span/text()').extract_first():
                        item['movement'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Straps" in tr.xpath('./span/text()').extract_first():
                        item['bracelet_color'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Case" in tr.xpath('./span/text()').extract_first():
                        item['case_material'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue
                
                try:
                    if "Style of watch" in tr.xpath('./span/text()').extract_first():
                        item['clasp_type'] = tr.xpath('./span/text()').extract()[1]
                except:
                    continue

            yield item
        except:
            pdb.set_trace()
            pass
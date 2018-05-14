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

class VestiairecollectiveSpider(scrapy.Spider):
    name = "vestiairecollective"

    request_url = "https://us.vestiairecollective.com/api/?m=listProduct&a=int_js&h=5fcdc0ac04537595a747e2830037cca0&u=4stor&v=1&lang=en&currency=USD&id_site=6&withNumberOfHitsPerFilter=1&limit=##limit##&fast=fast&id_page%5B%5D=44&id_page%5B%5D=164&substate%5B%5D=17&step=##step##"
    base_url = "https://us.vestiairecollective.com/"
    storeNumbers = []

    def start_requests(self):
        limit = 0
        while limit < 4600:
            yield scrapy.Request(url=self.request_url.replace('##limit##', str(limit)).replace('##step##', str(1000)))
            limit += 1000

    def parse(self, response):        
        items = json.loads(response.body)['result']['listProduct']
        for item in items:
            if item['rawPrice'] < 1000:
                continue

            if 'notSold' in item:
                yield scrapy.Request(url=self.base_url + item['ezlink'] + '.shtml', callback=self.parse_watch)

    def parse_watch(self, response):
        item = ChainItem()
        try:
            name = response.xpath('//*[@itemprop="name"]/@content').extract_first()
            item['website_id'] = response.xpath('//input[@name="productID"]/@value').extract_first()
            item['watchr_id'] = "empty"
            item['shop_id'] = "Shop4"
            item['sku'] = "empty"
            item['brand'] = response.xpath('//h1[@class="prd-title"]//span[@itemprop="brand"]/text()').extract_first()
            item['ref'] = item['website_id']
            item['model'] = response.xpath('//h1[@class="prd-title"]//span[@itemprop="name"]/text()').extract_first().strip()
            item['price'] = response.xpath('//p[@itemprop="offers"]/span[@itemprop="price"]/@content').extract_first()
            item['watchr_price'] = ''
            item['currency'] = response.xpath('//p[@itemprop="offers"]/span[@itemprop="priceCurrency"]/@content').extract_first()
            item['dealer_link'] = response.url
            image_urls = response.xpath('//div[@id="prd_gallery"]//li/button/@data-src').extract()

            item['img_link'] = "" + ', '.join(image_urls) + ""

            item['description'] = response.xpath('//meta[@property="og:description"]/@content').extract_first()
            item['exp_description'] = response.xpath('//meta[@name="twitter:description"]/@content').extract()
            item['gemstones'] = ''
            
            tr_list = response.xpath('//ul[@id="details_list1"]//li')

            for tr in tr_list:
                try:
                    if "matiere" in tr.xpath('./@id').extract_first():
                        item['clasp_material'] = tr.xpath('./a/text()').extract_first()
                except:
                    continue

                try:
                    if "couleur" in tr.xpath('./@id').extract_first():
                        item['bracelet_color'] = tr.xpath('./a/text()').extract_first()
                except:
                    continue

                try:
                    if "m_bracelet" in tr.xpath('./@id').extract_first():
                        item['bracelet_material'] = tr.xpath('.//text()').extract()[0].strip()
                except:
                    continue
                
                try:
                    if "boite_origine" in tr.xpath('./@id').extract_first():
                        item['box'] = tr.xpath('.//text()').extract()[0].strip()
                except:
                    continue
                
                try:
                    if "papier_origine" in tr.xpath('./@id').extract_first():
                        item['papers'] = tr.xpath('.//text()').extract()[0].strip()
                except:
                    continue

            yield item
        except:
            pdb.set_trace()
            pass
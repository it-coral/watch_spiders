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
from translate import translator
from googleapiclient.discovery import build
from chainxy.settings import GOOGLE_API_KEY
service = build('translate', 'v2', developerKey=GOOGLE_API_KEY)

class WatchesdeSpider(scrapy.Spider):
    name = "watchesde"    
    base_url = "https://www.watch.de"
    request_url = "https://www.watch.de/english/rolex.html?limit=120&p=###page###"

    product_urls = []
    pages = 7
    is_get_all = False
    models = ['Datejust','Oyster Perpetual', 'Sea-Dweller','Daytona', 'Cellini', 'Day Date', 'Explorer', 'Oysterdate Precision', 'Submariner', 'GMT Master', 'Precision', 'Air King', 'Oyster Cocktail', 'Yacht-Master', 'Deepsea', 'Perlmaster', 'Sky-Dweller' ]

    def start_requests(self):
        for index in range(0, self.pages):
            yield scrapy.Request(url=self.request_url.replace('###page###', str(index+1)))


    def parse(self, response):
        items = response.xpath("//ul[contains(@class, 'products-grid-in clearfix')]//li[contains(@class, 'item')]")
        for item in items:
            price = item.xpath(".//span[@class='price']/text()").extract_first()
            try:
                price = int(filter(str.isdigit, price.encode('utf-8')))
            except Exception as e:
                continue

            if price < 1000:
                continue

            url = item.xpath(".//div[@class='product-name']/a/@href").extract_first()
            yield scrapy.Request(url=url, callback=self.parse_watch)

    def parse_watch(self, response):        
        item = ChainItem()

        try:
            name = response.xpath('//title/text()').extract_first()

            item['website_id'] = response.xpath("//input[@name='product']/@value").extract_first()
            item['watchr_id'] = "empty"
            item['shop_id'] = "Shop3"
            item['sku'] = "empty"
            item['brand'] = 'Rolex'
            item['model'] = ''

            for model in self.models:
                if model in name:
                    item['model'] = model


            if item['model'] is '':
                return

            item['price'] = response.xpath('//div[@class="product-shop-1"]//span[@class="price"]/text()').extract_first()
            item['price'] = int(filter(str.isdigit, item['price'].encode('utf-8')))
            item['currency'] = 'EUR'
            item['watchr_price'] = ''

            item['dealer_link'] = response.url
            
            image_urls = response.xpath('//div[@class="product-img-box"]//a[@class="jqzoom"]/@href').extract()
            item['img_link'] = "" + ', '.join(image_urls) + ""
            
            item['description'] = ''
            item['exp_description'] = ''
            item['gemstones'] = ''
            
            # pdb.set_trace()
            tr_list = response.xpath('//table[@id="product-attribute-specs-table"]//tr')
            
            for tr in tr_list:
                
                try:
                    if "movement" in tr.xpath('./th/text()').extract_first():
                        item['movement'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue

                try:
                    if "case" in tr.xpath('./th/text()').extract_first():
                        item['clasp_material'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue

                try:
                    if "reference" in tr.xpath('./th/text()').extract_first():
                        item['ref'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue

                try:
                    if "diameter" in tr.xpath('./th/text()').extract_first():
                        item['case_size'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue

                try:
                    if "crystal" in tr.xpath('./th/text()').extract_first():
                        item['crystal'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue


                try:
                    if "box" in tr.xpath('./th/text()').extract_first():
                        item['box'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue

                try:
                    if "condition" in tr.xpath('./th/text()').extract_first():
                        item['description'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue

                try:
                    if "Garantie" in tr.xpath('./th/text()').extract_first():
                        item['exp_description'] = 'Including Watch.de watch pass & JRH 1000 days warranty'
                except:
                    continue


                try:
                    if "bracelet" in tr.xpath('./th/text()').extract_first():
                        item['bracelet_material'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue
                
                try:
                    if "papers" in tr.xpath('./th/text()').extract_first():
                        item['papers'] = tr.xpath('./td/text()').extract_first().strip()
                except:
                    continue

            yield item
        except:
            return
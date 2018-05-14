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
from googleapiclient.discovery import build
from chainxy.settings import GOOGLE_API_KEY
service = build('translate', 'v2', developerKey=GOOGLE_API_KEY)

class CavourorologiSpider(scrapy.Spider):
    name = "cavourorologi"

    request_url = "https://www.cavourorologi.it/nuovi-arrivi?p=##page##"
    storeNumbers = []
    pages = 4
    base_url = "https://www.cavourorologi.it/"

    def start_requests(self):
        for index in range(0, self.pages):
            yield scrapy.Request(url=self.request_url.replace('##page##', str(index+1)))


    def parse(self, response):
        items = response.xpath('//div[@id="items"]/div[@class="item"]')
        for item in items:
            url = item.xpath('.//a[@class="button"]/@href').extract_first()
            yield scrapy.Request(url=url, callback=self.parse_watch)

    def parse_watch(self, response):
        item = ChainItem()
        
        try:
            name = response.xpath('//div[@id="product-main"]/div[@class="heading"]//text()').extract()
            name = [tp.strip() for tp in name if tp.strip() != ""]
            item['website_id'] = response.xpath('//input[@id="id_orologio"]/@value').extract_first()
            item['watchr_id'] = "empty"
            item['shop_id'] = "Shop6"
            item['sku'] = "empty"
            item['brand'] = name[0].strip()
            item['ref'] = name[2].split(' ')[1].strip()
            item['model'] = name[1].strip()
            item['price'] = response.xpath('//input[@name="importo"]/@value').extract_first()[:-2]

            if int(item['price']) <= 1000:
                return
            
            item['watchr_price'] = ''
            item['currency'] = 'EUR'

            item['dealer_link'] = response.url
            image_urls = response.xpath('////a[@data-slide-id="zoom"]/@data-image').extract()

            item['img_link'] = "" + ', '.join(image_urls) + ""

            item['description'] = response.xpath('//div[@class="description"]/p/text()').extract_first()
            item['exp_description'] = ''
            item['gemstones'] = ''
            
            dt_list = response.xpath('//dl[@class="data-sheet"]//dt')
            dd_list = response.xpath('//dl[@class="data-sheet"]//dd')

            for index, tr in enumerate(dt_list):
                try:
                    if "Anno" in tr.xpath('./text()').extract_first():
                        item['year'] = dd_list[index].xpath('./text()').extract_first().strip()
                except:
                    continue

                if "Carica" in tr.xpath('./text()').extract_first():
                    item['movement'] = dd_list[index].xpath('./text()').extract_first().strip()

                if "Misura" in tr.xpath('./text()').extract_first():
                    item['case_size'] = dd_list[index].xpath('./text()').extract_first().strip()

                if "Cassa" in tr.xpath('./text()').extract_first():
                    item['case_material'] = dd_list[index].xpath('./text()').extract_first().strip()

                if "Cinturino" in tr.xpath('./text()').extract_first():
                    item['bracelet_material'] = dd_list[index].xpath('./text()').extract_first().strip()

                if "Quadrante" in tr.xpath('./text()').extract_first():
                    item['dial_color'] = dd_list[index].xpath('./text()').extract_first().strip()

                if "Vetro" in tr.xpath('./text()').extract_first():
                    item['crystal'] = dd_list[index].xpath('./text()').extract_first().strip()
                
                if "Scatola" in tr.xpath('./text()').extract_first():
                    item['box'] = dd_list[index].xpath('./text()').extract_first().strip()

            translated_list = service.translations().list(source='it',target='en',q=[item['brand'], item['model'], item['ref'], item['description'], item['case_material'], item['bracelet_material'], item['box'], item['movement'], item['crystal']]).execute()
            time.sleep(1)

            item['brand'] = translated_list['translations'][0]['translatedText'] 
            item['model'] = translated_list['translations'][1]['translatedText']
            item['ref'] = translated_list['translations'][2]['translatedText']
            item['description'] = translated_list['translations'][3]['translatedText']
            item['case_material'] = translated_list['translations'][4]['translatedText']
            item['bracelet_material'] = translated_list['translations'][5]['translatedText']
            item['box'] = translated_list['translations'][6]['translatedText']
            item['movement'] = translated_list['translations'][7]['translatedText']
            item['crystal'] = translated_list['translations'][8]['translatedText']

            yield item
        except:
            pass
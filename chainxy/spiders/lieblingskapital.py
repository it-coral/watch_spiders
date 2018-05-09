# -*- coding: utf-8 -*-
# 
from __future__ import unicode_literals
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

class LieblingskapitalSpider(scrapy.Spider):
    name = "lieblingskapital"

    start_urls = ["https://www.lieblingskapital.de/collections/uhren"]
    base_url = "https://www.lieblingskapital.de"

    def parse(self, response):
        column_list = response.xpath('//div[@class="columns__column shop_category__products_list_item"]')

        for column in column_list:

            if 'Nicht' in column.xpath('.//span[@class="product_preview__availability"]/text()').extract_first():
                continue

            url = column.xpath('./a/@href').extract_first()
            yield scrapy.Request(url=self.base_url + url, callback=self.parse_watch)

    def parse_watch(self, response):
        item = ChainItem()

        try:
            name = response.xpath('//*[@itemprop="name"]/@content').extract_first()
            
            item['watchr_id'] = ""
            item['shop_id'] = "Shop9"
            item['sku'] = ""
            item['price'] = response.xpath('//meta[@property="og:price:amount"]/@content').extract_first().replace('.00', '').replace(',', '')

            if int(item['price']) < 1000:
                return
            
            item['watchr_price'] = ''
            item['currency'] = response.xpath('//meta[@property="og:price:amount"]/@content').extract_first()
            item['dealer_link'] = response.url
            image_urls = response.xpath('(//div[@class="shop_product__overview__gallery__thumbnails--wrapper"])[1]/div/@data-src').extract()

            images = []
            for image in image_urls:
                images.append('https:' + image.strip().split('?')[0])

            item['img_link'] = '"' + ', '.join(images) + '"'

            dd_list = response.xpath('//dl[@class="shop_product__details__specifications"]//dd')
            key_list = response.xpath('//dl[@class="shop_product__details__specifications"]//dh/text()').extract()
            item['brand'] = ''
            item['model'] = ''
            item['ref'] = ''
            item['description'] = ''
            item['case_material'] = ''
            item['bracelet_material'] = ''
            item['box'] = 'no'
            item['papers'] = 'no'
            item['movement'] = ''
            item['crystal'] = ''
            item['clasp_material'] = ''

            for index, dh in enumerate(key_list):
                try:
                    if 'Artikelnummer' in dh:
                        try:
                            item['website_id'] = dd_list[index].xpath('./text()').extract_first()
                        except:
                            item['website_id'] = ''
                        continue

                    if 'Hersteller' in dh:
                        item['brand'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Modell' in dh:
                        item['model'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Referenz' in dh:
                        item['ref'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Alter' in dh:
                        item['year'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Ziffernblatt' in dh:
                        item['dial_color'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Durchmesser' in dh:
                        item['case_size'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Zustand' in dh:
                        item['description'] = dd_list[index].xpath('./text()').extract_first().replace(',', ' ')
                        continue
                    if 'Material Gehäuse'.encode('utf8') in dh.encode('utf8'):
                        item['case_material'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Material Band' in dh:
                        item['bracelet_material'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Box' in dh:
                        item['box'] = dd_list[index].xpath('./text()').extract_first().replace('Ja', 'yes')
                        continue
                    if 'Papiere' in dh:
                        item['papers'] = dd_list[index].xpath('./text()').extract_first().replace('Ja', 'yes')
                        continue
                    if 'elevator' in dh:
                        item['movement'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Glas' in dh:
                        item['crystal'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                    if 'Material Lünette'.encode('utf8') in dh.encode('utf8'):
                        item['clasp_material'] = dd_list[index].xpath('./text()').extract_first()
                        continue
                except Exception as e:
                    pdb.set_trace()

            translated_list = service.translations().list(source='de',target='en',q=[item['brand'], item['model'], item['ref'], item['description'], item['case_material'], item['bracelet_material'], item['box'], item['papers'], item['movement'], item['crystal'], item['clasp_material']]).execute()
            time.sleep(1)

            item['brand'] = translated_list['translations'][0]['translatedText'] 
            item['model'] = translated_list['translations'][1]['translatedText']
            item['ref'] = translated_list['translations'][2]['translatedText']
            item['description'] = translated_list['translations'][3]['translatedText']
            item['case_material'] = translated_list['translations'][4]['translatedText']
            item['bracelet_material'] = translated_list['translations'][5]['translatedText']
            item['box'] = translated_list['translations'][6]['translatedText']
            item['papers'] = translated_list['translations'][7]['translatedText']
            item['movement'] = translated_list['translations'][8]['translatedText']
            item['crystal'] = translated_list['translations'][9]['translatedText']
            item['clasp_material'] = translated_list['translations'][10]['translatedText']

            yield item
        except Exception as e:
            pdb.set_trace()


    def parse_download(self, response):
        item = response.meta['item']
        file_name = item['common_name'] + "_" + item['cat_nr'] + ".mp3"
        item['mp3_file'] = file_name
        with open(file_name, 'wb') as f:
            f.write(response.body)

        yield item
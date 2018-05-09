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

class FilipucciSpider(scrapy.Spider):
    name = "filipucci"

    start_urls = ["http://www.filipucci.nl/en/watches/?filter%5B%5D=305267"]
    request_url = "http://www.filipucci.nl/en/watches/page##number##.html?filter%5B0%5D=305267"
    storeNumbers = []
    base_url = "http://www.filipucci.nl/en/"

    def parse(self, response):
        total_page = int(response.xpath('//div[@class="pager row"]/ul/li[7]/a/text()').extract_first())
        index = 1
        while index < total_page+1:
            yield scrapy.Request(url=self.request_url.replace('##number##', str(index)), callback=self.parse_watch_list)
            index += 1

    def parse_watch_list(self, response):
        watch_list = response.xpath('//div[@class="product col-xs-6 col-sm-3 col-md-3"]/div[@class="info"]/a/@href').extract()

        for url in watch_list:
            yield scrapy.Request(url=url, callback=self.parse_watch)

    def parse_watch(self, response):
        item = ChainItem()

        try:
            name = response.xpath('//*[@itemprop="name"]/@content').extract_first()
            item['website_id'] = response.xpath('//div[@class="copyright col-md-6"]/a/@href').extract_first().split('/')[-1]
            item['watchr_id'] = ""
            item['shop_id'] = "Shop8"
            item['sku'] = ""
            item['brand'] = name.split(' ')[0]
            item['ref'] = name.split(' ')[-1]
            item['model'] = name.replace(item['brand'], '').replace(item['ref'], '').strip()
            item['price'] = response.xpath('//*[@itemprop="price"]/@content').extract_first().replace('.00', '').replace('.', '')

            if int(item['price']) <= 1000:
                return
            
            item['watchr_price'] = ''
            item['currency'] = response.xpath('//*[@itemprop="currency"]/@content').extract_first()
            item['dealer_link'] = response.url
            image_urls = response.xpath('//*[@class="images"]//img/@src').extract()
            
            images = []
            for image in image_urls:
                images.append('https:' + image.strip().split('?')[0])

            item['img_link'] = '"' + ', '.join(images) + '"'

            item['description'] = response.xpath('//*[@itemprop="description"]/@content').extract_first()
            item['exp_description'] = ', '.join(response.xpath('//ul[@class="usps"]/li//text()').extract())
            item['gemstones'] = ''
            
            tr_list = response.xpath('//table[@class="tb"]//tr')

            for tr in tr_list:
                try:
                    if "Year:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                        item['year'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()
                except:
                    continue

                if "Original Box:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['box'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()
                
                if "Reference Number:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['ref'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Original Papers:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['papers'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Movement Type:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['movement'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Case Diameter:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['case_size'] = tr.xpath('./td[@class="tbv"]/text()').extract_first().replace('mm', '')

                if "Case Material:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['case_material'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Bracelet Color:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['bracelet_color'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Bracelet Material:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['bracelet_material'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Crystal:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['crystal'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Dial Color: " in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['dial_color'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Clasp Material:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['clasp_material'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()

                if "Clasp:" in tr.xpath('./td[@class="tbh"]/text()').extract_first():
                    item['clasp_type'] = tr.xpath('./td[@class="tbv"]/text()').extract_first()


            yield item
        except:
            pass
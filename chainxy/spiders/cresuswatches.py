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

class CresuswatchesSpider(scrapy.Spider):
    name = "cresuswatches"

    start_urls = ["https://www.cresuswatches.com/adjnav/ajax/category/id/3/?dir=desc&order=price&no_cache=true&home=0&limit=150&p=1&no_cache=true&home=0"]
    base_url = "https://www.lieblingskapital.de"
    request_url = "https://www.cresuswatches.com/adjnav/ajax/category/id/3/?dir=desc&order=price&no_cache=true&home=0&limit=150&p=@@index@@&no_cache=true&home=0"

    product_urls = []
    page = 1
    is_get_all = False

    def parse(self, response):
        body = etree.HTML(json.loads(response.body)['products'])
        column_list = body.xpath('//div[contains(@class, "col-item item")]')

        for column in column_list:
            if len(column.xpath('.//div[@class="itImg"]/span[@class="statusArticle"]')) == 0:
                price = column.xpath('.//div[@class="price-box"]//span[@class="price"]/text()')[0]
                price = int(filter(str.isdigit, price.encode('utf8')))
                if price > 1000:
                    url = column.xpath('.//a[@class="itLink"]/@href')[0]
                    self.product_urls.append(url)
            else:
                self.is_get_all = True
                break

        if self.is_get_all:
            for url in self.product_urls:
                yield scrapy.Request(url=url, callback=self.parse_watch)
        else:
            self.page += 1
            yield scrapy.Request(url=self.request_url.replace('@@index@@', str(self.page)))

    def parse_watch(self, response):
        # pdb.set_trace()
        item = ChainItem()

        try:
            name = response.xpath('//*[@itemprop="name"]/@content').extract_first()            
            item['watchr_id'] = ""
            item['shop_id'] = "Shop10"
            item['sku'] = ""
            item['brand'] = response.xpath('//h1[@itemprop="brand"]/a/text()').extract_first()

            item['price'] = response.xpath('//meta[@itemprop="price"]/@content').extract_first()
            item['currency'] = response.xpath('//*[@itemprop="priceCurrency"]/@content').extract_first()

            item['watchr_price'] = ''

            item['dealer_link'] = response.url
            
            image_urls = response.xpath('//div[@id="productImageContainer"]//img[@itemprop="image"]/@src').extract()

            images = []
            for image in image_urls:
                images.append('https:' + image.strip().split('?')[0])

            item['img_link'] = '"' + ', '.join(images) + '"'
            
            item['description'] = response.xpath('//span[@itemprop="description"]/text()').extract_first()
            item['model'] = response.xpath('//meta[@itemprop="name"]/@content').extract_first().replace(item['brand'], '').strip()

            model = service.translations().list(source='fr',target='en',q=[item['model'], item['description']]).execute()
            time.sleep(1)

            item['model'] = model['translations'][0]['translatedText']
            item['description'] = model['translations'][1]['translatedText'].replace(',', ' ')

            item['exp_description'] = ''
            item['gemstones'] = ''
            
            tr_list = response.xpath('//div[@class="listAdditional"]')
            
            for tr in tr_list:
                
                try:
                    if "movement" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        item['movement'] = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                except:
                    continue
                
                try:
                    if "Cresus ref" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        item['website_id'] = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                except:
                    continue

                try:
                    if "Model case" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        item['dial_color'] = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                except:
                    continue
                
                try:
                    if "Bracelet" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        item['bracelet_material'] = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                except:
                    continue
                
                try:
                    if "Buckle" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        item['clasp_material'] = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                except:
                    continue
                
                try:
                    if "Dimensions" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        item['case_size'] = tr.xpath('./span[@class="data"]/text()').extract_first().replace('mm', '').strip()
                except:
                    continue

                try:
                    if "Year" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        year = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                        item['year'] = int(filter(str.isdigit, year))
                except:
                    continue


                try:
                    if "Manufacturer Ref" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        item['ref'] = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                except:
                    continue
                    
                try:
                    if "Box" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        if "Original" in tr.xpath('./span[@class="data"]/text()').extract_first():
                            item['box'] = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                        else:
                            item['box'] = "no"
                except:
                    item['box'] = "no"

                try:
                    if "Documents" in tr.xpath('./span[@class="label"]/text()').extract_first():
                        if "Original" in tr.xpath('./span[@class="data"]/text()').extract_first():
                            item['papers'] = tr.xpath('./span[@class="data"]/text()').extract_first().strip()
                        else:
                            item['papers'] = "no"
                except:
                    item['papers'] = "no"

                    
                item['bracelet_color'] = ''
                item['crystal'] = ''
                item['clasp_type'] = ''


            yield item
        except:
            pdb.set_trace()
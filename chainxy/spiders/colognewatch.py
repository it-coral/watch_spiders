import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

from lxml import etree
import time
import pdb
from translate import translator
from googleapiclient.discovery import build
from chainxy.settings import GOOGLE_API_KEY
service = build('translate', 'v2', developerKey=GOOGLE_API_KEY)

class ColognewatchSpider(scrapy.Spider):
    name = "colognewatch"    
    base_url = "https://www.colognewatch.de/?___store=english&___from_store=german"
    request_url = "https://www.colognewatch.de/watches?p=###page###"

    product_urls = []
    pages = 48
    is_get_all = False
    max_delay_limit = 10

    start_urls = ['https://www.google.com/']
    def parse(self, response):
        driver = webdriver.Chrome("./chromedriver")
        driver.get(self.base_url)

        for index in range(0, self.pages):
            driver.get(self.request_url.replace('###page###', str(index+1)))
            content = etree.HTML(driver.page_source.encode('utf8'))
            items = content.xpath("//div[contains(@class, 'products wrapper grid products-grid')]/a")

            for item in items:
                price = item.xpath(".//span[contains(@class,'price-wrapper')]/@data-price-amount")[0]
                try:
                    price = int(filter(str.isdigit, price.encode('utf-8')))
                except Exception as e:
                    continue

                if price < 1000:
                    continue

                url = item.xpath("./@href")[0]
                driver.get(url)
                detail_content = etree.HTML(driver.page_source.encode('utf8'))
                
                item = ChainItem()

                try:
                    item['website_id'] = url.split('-')[-1]
                    item['watchr_id'] = "empty"
                    item['shop_id'] = "Shop11"
                    item['sku'] = "empty"
                    item['brand'] = detail_content.xpath("//main[@id='maincontent']//span[@class='fd_brand']/text()")[0]
                    item['model'] = detail_content.xpath("//main[@id='maincontent']//span[@class='fd_model']/text()")[0]

                    try:
                        item['ref'] = detail_content.xpath("//main[@id='maincontent']//span[@class='fd_mpn']/text()")[0]
                    except:
                        item['ref'] = ''

                    item['price'] = detail_content.xpath('//meta[@property="product:price:amount"]/@content')[0]
                    item['currency'] = detail_content.xpath('//meta[@property="product:price:currency"]/@content')[0]

                    item['watchr_price'] = ''
                    item['dealer_link'] = url
                    
                    image_urls = detail_content.xpath('//div[@class="product-unused media-unused"]//div[@class="fd_col fd_col-7 fd_offset-col-5 fd_m-col-6 fd_m-offset-col-6 fd_s-col-12 fd_s-offset-col-0 fd_product-imgs fd_is-hidden-s"]//img[@class="fd_intense-zoom"]/@data-image')

                    item['img_link'] = "" + ', '.join(image_urls) + ""
                    
                    item['description'] = ''
                    item['exp_description'] = ''
                    item['gemstones'] = ''
                    
                    # pdb.set_trace()
                    tr_list = detail_content.xpath("//table[@class='fd_product-specs-table']//tr")
                    
                    for tr in tr_list:
                        
                        try:
                            if "Clockwork" in tr.xpath('./th/text()')[0]:
                                item['movement'] = tr.xpath('./td/text()')[0].strip()
                        except:
                            pdb.set_trace()
                            continue

                        try:
                            if "CW Article No." in tr.xpath('./th/text()')[0]:
                                item['website_id'] = tr.xpath('./td/text()')[0].strip()
                        except:
                            pdb.set_trace()
                            continue

                        try:
                            if "Case" in tr.xpath('./th/text()')[0]:
                                item['clasp_material'] = tr.xpath('./td/text()')[0].strip()
                        except:
                            pdb.set_trace()
                            continue

                        try:
                            if "Diameter" in tr.xpath('./th/text()')[0]:
                                item['case_size'] = tr.xpath('./td/text()')[0].strip()
                        except:
                            pdb.set_trace()
                            continue

                        try:
                            if "Dial" in tr.xpath('./th/text()')[0]:
                                item['dial_color'] = tr.xpath('./td/text()')[0].strip()
                        except:
                            pdb.set_trace()
                            continue

                        try:
                            if "Glass" in tr.xpath('./th/text()')[0]:
                                item['crystal'] = tr.xpath('./td/text()')[0].strip()
                        except:
                            pdb.set_trace()
                            continue


                        try:
                            if "Scope of delivery" in tr.xpath('./th/text()')[0]:
                                text = tr.xpath('./td/text()')[0].strip()

                                if 'Original box' in text:
                                    item['box'] = 'yes'
                                else:
                                    item['box'] = 'no'

                                if 'Original documents' in text:
                                    item['papers'] = 'yes'
                                else:
                                    item['papers'] = 'no'

                        except:
                            pdb.set_trace()
                            continue

                        try:
                            if "Year" in tr.xpath('./th/text()')[0]:
                                item['year'] = tr.xpath('./td/text()')[0].strip()
                        except:
                            pdb.set_trace()
                            continue

                        try:
                            if "Strap" in tr.xpath('./th/text()')[0]:
                                item['bracelet_material'] = tr.xpath('./td/text()')[0].strip()
                        except:
                            pdb.set_trace()
                            continue                

                    yield item
                except:
                    pdb.set_trace()
                    pass
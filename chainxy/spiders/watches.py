# -*- coding: utf-8 -*-
import scrapy, logging, datetime
from chainxy.items import ChainItem
from scrapy.utils.log import configure_logging

class WatchesSpider(scrapy.Spider):
    name = 'collectorsquare'
    allowed_domains = ['collectorsquare.com/en/']
    start_urls = ['https://www.collectorsquare.com/en/watches.html?limit=90'] #90
    site_link = 'https://www.collectorsquare.com%s'
    image_link = 'https://www.collectorsquare.com/ajax-zoom/pic/zoomthumb/%s/%s/%s-hd-%s_600x400.jpg'
    configure_logging(install_root_handler=False)
    now = datetime.datetime.now()
    
    def parse(self, response):
        watches=response.xpath('//li[contains(@class,"product col-sm-4 col-xs-6")]')
        for watch in watches:
            item = ChainItem()
            item['watchr_id'] = "empty"
            item['sku'] = "empty"
            item['website_id'] = watch.xpath('@data-product-code').extract_first()
            item['brand'] = watch.xpath('.//p[@class="brand"]//span/text()').extract_first()
            #item['model'] = watch.xpath('.//div[@class="name"]//span/text()').extract_first()
            item['img_link'] = self.site_link % (watch.xpath('.//img/@src').extract_first())
            url = watch.xpath('.//meta/@content').extract_first()
            item['dealer_link'] = url
            yield scrapy.Request(url, callback = self.parse_watch, dont_filter=True
                                 , headers={'Content-Type': 'application/json','charset':'UTF-8'}
                                 , meta={'item':item}
                     )

        next_url = response.xpath('//a[@rel="next"]/@href').extract_first()
        self.log('### Next URL: '+next_url+' ###')
        if next_url:
            next_url = self.site_link % next_url
            yield scrapy.Request(next_url, callback = self.parse, dont_filter=True)
            
    def parse_watch(self, response):
        item = response.meta['item']
        #item['ref'] = response.xpath('//p[@class="ref"]/text()').extract_first().replace('Collector Square Ref: ','')
        item['price'] = response.xpath('//div[@class="price"]//span[@itemprop="price"]/@content').extract_first()
        item['currency'] = response.xpath('//div[@class="price"]//span[@itemprop="priceCurrency"]/@content').extract_first()
        item['description'] = response.xpath('//meta[@name="description"]/@content').extract_first().replace('\n', ' ').replace('\r', '')
        item['model'] = ''
        for col in response.xpath('//div[@class="col-xs-6"]'):
            for div in col.xpath('./div'):
                title = div.xpath('text()').extract_first()
                if 'Year :' in title:
                    item['year'] = div.xpath('./span/text()').extract_first()
                if 'Reference Detail :' in title:
                    item['ref'] = div.xpath('./span/text()').extract_first()                    
                if 'Model :' in title:
                    item['model'] = div.xpath('./span/text()').extract_first()
                if 'Period :' in title:
                    item['year'] = div.xpath('./span/text()').extract_first()
                if 'Case material :' in title:
                    item['case_material'] = div.xpath('./span/text()').extract_first()
                if 'Dial color :' in title:
                    item['dial_color'] = div.xpath('./span/text()').extract_first()
                if 'Movement :' in title:
                    item['movement'] = div.xpath('./span/text()').extract_first()
                if 'Bracelet color :' in title:
                    item['bracelet_color'] = div.xpath('./span/text()').extract_first()
                if 'Bracelet material :' in title:
                    item['bracelet_material'] = div.xpath('./span/text()').extract_first()  
                if 'Clasp type :' in title:
                    item['clasp_type'] = div.xpath('./span/text()').extract_first()
                if 'Certificate :' in title:
                    item['papers'] = div.xpath('./span/text()').extract_first()
                if 'Case :' in title:
                    item['box'] = div.xpath('./span/text()').extract_first()
                if 'Diameter :' in title:
                    item['case_size'] = div.xpath('./span/text()').extract_first()                    
                    
        if item['website_id']:
            f1 = item['website_id'][0:1]
            f2 = item['website_id'][1:2]
            item['img1_link'] = self.image_link % (f1, f2, item['website_id'], '0003')
            item['img2_link'] = self.image_link % (f1, f2, item['website_id'], '0009')
            item['img3_link'] = self.image_link % (f1, f2, item['website_id'], '0015')
        
        item['img_link'] = '%s, %s, %s, %s' % (item['img_link'], item['img1_link'], item['img2_link'], item['img3_link'])

        if not(item['model']):
            brand = response.xpath('//p[@class="brand"]/text()').extract_first()
            model = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
            if model:
                item['model']=model.replace(brand,"",1).rsplit('watch',1)[0]
            
        item['exp_description'] = ''
        desc_list=response.xpath('//div[@class="otsdescrcaract"]//*')
        for desc in desc_list:
            text = desc.xpath('text()').extract_first()
            item['exp_description'] = item['exp_description'] + text.replace('\n', ' ').replace('\r', '')
         
        cond_list=response.xpath('//div[@class="otsdescrcondition"]//*')
        for cond in reversed(cond_list):
            text = cond.xpath('text()').extract_first()
            item['exp_description'] = item['exp_description'] + text.replace('\n', ' ').replace('\r', '')          
                    
        yield item

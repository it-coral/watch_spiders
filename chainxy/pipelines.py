# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import time
import datetime
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
from slackclient import SlackClient
import tinys3
import settings
import pdb
from boto3.s3.transfer import S3Transfer
import boto3

credentials = { 
    'aws_access_key_id': settings.S3_ACCESS_KEY,
    'aws_secret_access_key': settings.S3_SECRET_KEY
}

class ChainxyPipeline(object):

    def __init__(self):
        self.files = {}
        self.file_names = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file_name = '%s_%s.csv' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d'))
        self.file_names[spider] = file_name
        file = open(file_name, 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = ["website_id","watchr_id","shop_id","sku","brand","model","ref","box","papers","year","description","movement","case_size","case_material","crystal","dial_color","gemstones","bracelet_material","bracelet_color","clasp_material","clasp_type","price","watchr_price","currency","dealer_link","img_link","img1_link","img2_link","img3_link","exp_description"]
        self.exporter.start_exporting()        

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()
        file_name = self.file_names.pop(spider)
        message = '%s file is ready' % file_name
        self.slack_message(message, '#web-scrapper')
        # print(self.upload_s3(file_name))

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def slack_message(self, message, channel):
        token = settings.SLACK_TOKEN
        sc = SlackClient(token)
        sc.api_call('chat.postMessage', channel=channel, 
                    text=message, username='Alert Scrapy Notitication',
                    icon_emoji=':robot_face:')

    def upload_s3(self, file_name):
        client = boto3.client('s3', 'us-west-2', **credentials)
        transfer = S3Transfer(client)
        transfer.upload_file(file_name, settings.BUCKET_NAME, file_name,
                             extra_args={'ACL': 'public-read'})
        return '%s/%s/%s' % (client.meta.endpoint_url, settings.BUCKET_NAME, file_name)

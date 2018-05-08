# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ChainItem(Item):
    website_id = Field()
    watchr_id = Field()
    shop_id = Field()
    sku = Field()
    brand = Field()
    model = Field()
    ref = Field()
    box = Field()
    papers = Field()
    year = Field()
    description = Field()
    movement = Field()
    case_size = Field()
    case_material = Field()
    crystal = Field()
    dial_color = Field()
    gemstones = Field()
    bracelet_material = Field()
    bracelet_color = Field()
    clasp_material = Field()
    clasp_type = Field()
    price = Field()
    watchr_price = Field()
    currency = Field()
    dealer_link = Field()
    img_link = Field()
    img1_link = Field()
    img2_link = Field()
    img3_link = Field()
    exp_description = Field()
    
    
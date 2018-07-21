# -*- coding: utf-8 -*-
import scrapy


class ReleasescrawlerItem(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    release_date = scrapy.Field()
    platform = scrapy.Field()
    tags = scrapy.Field()

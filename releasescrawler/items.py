# -*- coding: utf-8 -*-
import scrapy


class ReleasescrawlerItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    tags = scrapy.Field()
    release_version = scrapy.Field()
    release_country = scrapy.Field()
    release_date_string = scrapy.Field()
    release_date = scrapy.Field()
    release_status = scrapy.Field()
    release_platform = scrapy.Field()

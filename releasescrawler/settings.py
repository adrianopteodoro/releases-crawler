# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

BOT_NAME = 'releasescrawler'

SPIDER_MODULES = ['releasescrawler.spiders']
NEWSPIDER_MODULE = 'releasescrawler.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
ROBOTSTXT_OBEY = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 701,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 702
}

ITEM_PIPELINES = {
    'releasescrawler.pipelines.ReleasescrawlerPipeline': 300,
}

LOG_LEVEL = 'INFO'
# LOG_LEVEL = 'DEBUG'

# Custom settings
MONGODB = {
    'username': os.getenv('MONGODB_USER').strip('\n'),
    'password': os.getenv('MONGODB_PWD').strip('\n'),
    'database': os.getenv('MONGODB_DATABASE').strip('\n'),
    'url': os.getenv('MONGODB_URL').strip('\n'),
}

# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from releasescrawler.items import ReleasescrawlerItem


class ReleasesException(Exception):
    pass


class ReleasesSpider(CrawlSpider):
    name = 'releases'
    allowed_domains = ['releases.com']
    restricted_xpaths = [
        '//*[contains(@class,\'calendar-item-title subpage-trigg\')]'
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow=(),
                restrict_xpaths=restricted_xpaths,
            ),
            callback='parse_links',
            follow=False,
        ),
    )

    def __init__(self, *a, **kw):
        self.log = logging.getLogger(self.name)
        self.start_urls = self.get_start_urls()
        super(ReleasesSpider, self).__init__(*a, **kw)

    def get_start_urls(self):
        start_urls = []
        current_year = datetime.now().year
        current_month = datetime.now().month
        for x in range(0, (12 - current_month) + 1):
            start_urls.append(
                'https://www.releases.com/l/Games/{year}/{month}/'.format(
                    year=current_year,
                    month=int(current_month + x)
                )
            )
        self.log.info('start_urls:\n%s', '\n'.join(start_urls))
        return start_urls

    def get_xpathstring(self, response, xpath_str, str_sep='\x20'):
        return str_sep.join(response.xpath(xpath_str).extract())

    def parse_links(self, response):
        try:
            self.log.info('url: %s', response.url)
            name = self.get_xpathstring(
                response, '//*[contains(@itemprop, \'name\')]/text()'
            )
            item = ReleasescrawlerItem()
            item['name'] = name
            yield item
        except ReleasesException as ex:
            self.log.exception('%s', ex)

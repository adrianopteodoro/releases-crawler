# -*- coding: utf-8 -*-
import hashlib
import logging
import re
from datetime import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule

from releasescrawler.items import ReleasescrawlerItem


class ReleasesGamesException(Exception):
    pass


class ReleasesGamesSpider(CrawlSpider):
    name = 'releases_games'
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
        super(ReleasesGamesSpider, self).__init__(*a, **kw)

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

    def get_xpathstring(self, content, xpath_str, str_sep='\x20'):
        return str_sep.join(content.xpath(xpath_str).extract()).strip()

    def get_countryfromflag(self, content_path):
        regex = r'.*\-([a-zA-Z]+)\..*'
        found = re.findall(regex, content_path)
        return ''.join(found)

    def parse_links(self, response):
        try:
            name = self.get_xpathstring(
                response, '//*[contains(@itemprop, \'name\')]/text()'
            )
            description = self.get_xpathstring(
                response, '//*[contains(@itemprop, \'description\')]/text()'
            )
            tags = response.xpath(
                '//*[contains(@class, \'p-details-tags\')]/li/a/text()'
            ).extract()
            trackings = response.xpath(
                '//*[contains(@class, \'rl-row rl-tracking\')]'
            ).extract()
            for track in trackings:
                item = ReleasescrawlerItem()
                track_element = Selector(text=track)
                release_flag = self.get_xpathstring(
                    track_element,
                    '//*[contains(@class, \'date-region-flag\')]'
                )
                item['name'] = name
                item['description'] = description
                item['tags'] = tags
                item['release_version'] = self.get_xpathstring(
                    track_element,
                    '//*[contains(@class, \'rl-row rl-tracking\')]/@data-version-id'
                )
                item['release_country'] = self.get_countryfromflag(
                    release_flag
                )
                item['release_platform'] = self.get_xpathstring(
                    track_element,
                    '//*[contains(@class, \'version\')]/text()'
                )
                item['release_date'] = self.get_xpathstring(
                    track_element,
                    '//*[contains(@class, \'date-details\')]/span[contains(@class, \'date\')]/text()'
                )
                item['release_status'] = self.get_xpathstring(
                    track_element,
                    '//*[contains(@class, \'date-details\')]/span[contains(@class, \'status\')]/text()'
                )
                rid = '{name}:{platform}:{country}'.format(
                    name=name,
                    platform=item['release_platform'],
                    country=item['release_country']
                )
                item['rid'] = hashlib.sha256(str.encode(rid)).hexdigest()
                yield item
        except ReleasesGamesException as ex:
            self.log.exception('%s', ex)

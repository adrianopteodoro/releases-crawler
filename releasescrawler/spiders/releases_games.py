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
    months_ref = {
        'january': 1,
        'february': 2,
        'march': 3,
        'april': 4,
        'may': 5,
        'june': 6,
        'july': 7,
        'august': 8,
        'september': 9,
        'october': 10,
        'november': 11,
        'december': 12,
    }
    quarter_ref = {
        'q1': 1,
        'q2': 2,
        'q3': 3,
        'q4': 4,
    }
    quarter_months_ref = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12],
    }

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

    @staticmethod
    def get_quarter_month(month):
        if month in [1, 2, 3]:
            return 1
        if month in [4, 5, 6]:
            return 2
        if month in [7, 8, 9]:
            return 3
        if month in [10, 11, 12]:
            return 4

    def get_date_object(self, date_string):
        datestring_regex = r'(Q[0-9])\x20+([0-9]{4})|'\
            r'([A-Za-z]+)\x20+([0-9]{1,2})\,\x20+([0-9]{4})|'\
            r'([A-Za-z]+)\x20+([0-9]{4})|([0-9]{4})'
        founds = re.findall(datestring_regex, date_string)
        date_obj = {}
        for item in founds:
            quarter = self.quarter_ref.get(item[0].lower())
            month_str = item[2] if item[2] != '' else item[5]
            month = self.months_ref.get(month_str.lower())
            year = item[1] if item[1] != '' else item[4]\
                if item[4] != '' else item[6] if item[6] != '' else item[7]\
                if item[7] != '' else None
            day = item[3] if item[3] != '' else None
            if year:
                date_obj.update({'year': int(year)})
            if day:
                date_obj.update({'day': int(day)})
            if month:
                date_obj.update({'months': [month]})
            if not month and year:
                date_obj.update(
                    {'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]})
            if quarter:
                date_obj.update(
                    {'quarter': quarter, 'months': self.quarter_months_ref.get(quarter)})
            if not quarter and month:
                date_obj.update({'quarter': self.get_quarter_month(month)})
        return date_obj

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
                release_date_string = self.get_xpathstring(
                    track_element,
                    '//*[contains(@class, \'date-details\')]/span[contains(@class, \'date\')]/text()'
                )
                item['release_date_string'] = release_date_string
                item['release_date'] = self.get_date_object(
                    release_date_string)
                item['release_status'] = self.get_xpathstring(
                    track_element,
                    '//*[contains(@class, \'date-details\')]/span[contains(@class, \'status\')]/text()'
                )
                rid = '{name}:{platform}:{country}'.format(
                    name=name,
                    platform=item['release_platform'],
                    country=item['release_country']
                )
                item['_id'] = hashlib.sha256(str.encode(rid)).hexdigest()
                yield item
        except ReleasesGamesException as ex:
            self.log.exception('%s', ex)

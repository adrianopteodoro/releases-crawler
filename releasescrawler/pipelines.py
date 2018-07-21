# -*- coding: utf-8 -*-
import logging
import json


class ReleasescrawlerPipeline():
    def __init__(self):
        self.log = logging.getLogger('pipeline')

    def process_item(self, item, spider):
        self.log.info(
            'fromSpider: %s, item:\n%s',
            spider.name,
            json.dumps(dict(item), sort_keys=True, indent=4)
        )
        return item

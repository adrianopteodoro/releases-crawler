# -*- coding: utf-8 -*-
import logging

from pymongo import MongoClient
from pymongo.errors import PyMongoError


class PipelineException(Exception):
    pass


class ReleasescrawlerPipeline():
    def __init__(self, mongodb):
        self.log = logging.getLogger('pipeline')
        self.mongodb = mongodb

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb=crawler.settings.get('MONGODB')
        )

    def open_spider(self, spider):
        if self.mongodb is not None:
            if self.mongodb.get('url') is not None:
                if self.mongodb.get('username') is not None:
                    if self.mongodb.get('password') is not None:
                        if self.mongodb.get('database') is not None:
                            try:
                                self.client = MongoClient(
                                    self.mongodb.get('url'),
                                    username=self.mongodb.get('username'),
                                    password=self.mongodb.get('password'),
                                    authSource=self.mongodb.get('database')
                                )
                                self.db = self.client.get_database(
                                    name=self.mongodb.get('database')
                                )
                            except PyMongoError as ex:
                                self.log.error(
                                    'PyMongo Exception: %s',
                                    ex
                                )
                        else:
                            raise PipelineException(
                                'No database informatiion in mongodb dict from settings file'
                            )
                    else:
                        raise PipelineException(
                            'No password informatiion in mongodb dict from settings file'
                        )
                else:
                    raise PipelineException(
                        'No username informatiion in mongodb dict from settings file'
                    )
            else:
                raise PipelineException(
                    'No url informatiion in mongodb dict from settings file'
                )
        else:
            raise PipelineException(
                'No mongodb credentials dict in settings file'
            )

    def close_spider(self, spider):
        try:
            self.client.close()
        except PyMongoError as ex:
            self.log.error(
                'PyMongo Exception: %s',
                ex
            )

    def print_item(self, item, spider):
        self.log.info(
            'fromSpider: %s [%s, %s, %s, %s, %s]',
            spider.name,
            item['name'],
            item['release_platform'],
            item['release_country'],
            item['release_date'],
            item['release_status']
        )

    def process_item(self, item, spider):
        self.print_item(item, spider)
        collection = self.db.get_collection(name=spider.name)
        collection.find_one_and_delete({'_id': item['_id']})
        collection.insert_one(dict(item))
        return item

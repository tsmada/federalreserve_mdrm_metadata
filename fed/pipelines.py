# -*- coding: utf-8 -*-
import psycopg2 as pg
from psycopg2 import DataError, ProgrammingError, InternalError

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class FedPipeline(object):

    def __init__(self):
        self.files = {}
        self.conn = pg.connect(
          "dbname=fed user=acq password=tri05052009 host=192.168.200.31 port=5432")
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        print item, spider
        return item

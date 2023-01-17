  # Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime

import scrapy
from itemadapter import ItemAdapter

import json
import os

from crawler.footballdata.items import Data

BASE_PATH = "../data/"

class FootballdataJsonPipeline:
    def process_item(self, item, spider):
        if isinstance(item, Data):
            return self.handle_data(item, spider)
        return item

    def handle_data(self, item, spider):
        origin = item.get('origin')
        league_key = item.get('league_key')
        year = item.get('year')
        dir = f'{BASE_PATH}{origin}/{league_key}/{year}/'
        name = f'{dir}data.csv'
        self.mkdir(dir)
        file = open( name, 'wb' )
        file.write(item.get('raw').encode('utf-8'))
        return item

    def mkdir(self, path):
        is_dir = os.path.exists(path)
        if not is_dir:
            os.makedirs(path)


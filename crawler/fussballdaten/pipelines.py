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

from crawler.fussballdaten.items import Standings, Match

BASE_PATH = "../data/"

class FussballdatenPipeline:
    def process_item(self, item, spider):
        return item


def json_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    if isinstance(x, scrapy.Item):
        return dict(x)
    raise TypeError("Unknown type " + str(type(x)))


class FussballdatenJsonPipeline:
    def process_item(self, item, spider):
        if isinstance(item, Standings):
            return self.handle_standings(item, spider)
        if isinstance(item, Match):
            return self.handle_match(item, spider)
        return item

    def handle_standings(self, item, spider):
        content = json.dumps(dict(item), default=json_handler)
        fitem = item.get('standings')[0]
        origin = fitem.get('origin')
        league_key = fitem.get('league_key')
        year = fitem.get('year')
        matchday = fitem.get('matchday')
        if int(matchday) > 0:
            dir = f'{BASE_PATH}{origin}/{league_key}/{year}/{matchday}/'
            name = f'{dir}standings.json'
            self.mkdir(dir)
            file = open(name, 'wb')
            file.write(content.encode('utf-8'))
        return item

    def handle_match(self, item, spider):
        content = json.dumps(dict(item), default=json_handler)
        origin = item.get('origin')
        league_key = item.get('league_key')
        year = item.get('year')
        matchday = item.get('matchday')
        home_key = item.get('home_key')
        away_key = item.get('away_key')
        dir = f'{BASE_PATH}/{origin}/{league_key}/{year}/{matchday}/'
        name = f'{dir}{home_key}_{away_key}.json'
        self.mkdir(dir)
        file = open(name, 'wb')
        file.write(content.encode('utf-8'))
        return item

    def mkdir(self, path):
        is_dir = os.path.exists(path)
        if not is_dir:
            os.makedirs(path)


# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Data(scrapy.Item):
  # define the fields for your item here like:
  origin = scrapy.Field()
  year = scrapy.Field()
  season = scrapy.Field()
  league_key = scrapy.Field()
  league_name = scrapy.Field()
  raw = scrapy.Field()

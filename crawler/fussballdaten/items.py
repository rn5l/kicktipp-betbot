# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Standings(scrapy.Item):
  standings = scrapy.Field()

class Standing(scrapy.Item):
  # define the fields for your item here like:
  origin = scrapy.Field()
  year = scrapy.Field()
  season = scrapy.Field()
  matchday = scrapy.Field()
  league_key = scrapy.Field()
  league_name = scrapy.Field()
  place = scrapy.Field()
  team_key = scrapy.Field()
  team_name = scrapy.Field()
  points = scrapy.Field()
  goals = scrapy.Field()
  against = scrapy.Field()

class Match(scrapy.Item):
  # define the fields for your item here like:
  origin = scrapy.Field()
  year = scrapy.Field()
  season = scrapy.Field()
  matchday = scrapy.Field()
  date = scrapy.Field()
  league_key = scrapy.Field()
  league_name = scrapy.Field()
  link = scrapy.Field()
  source = scrapy.Field()

  home_key = scrapy.Field()
  home_name = scrapy.Field()
  home_short = scrapy.Field()
  home_goals = scrapy.Field()
  home_goals_ht = scrapy.Field()
  home_attemps = scrapy.Field()
  home_missed = scrapy.Field()
  home_freekicks = scrapy.Field()
  home_corners = scrapy.Field()
  home_offsite = scrapy.Field()
  home_fouls = scrapy.Field()
  home_held = scrapy.Field()
  home_possesion = scrapy.Field()
  home_passes = scrapy.Field()
  home_rating = scrapy.Field()
  home_tackles = scrapy.Field()
  home_yellow = scrapy.Field()
  home_red = scrapy.Field()
  home_players = scrapy.Field()
  home_tactic = scrapy.Field()

  away_key = scrapy.Field()
  away_name = scrapy.Field()
  away_short = scrapy.Field()
  away_goals = scrapy.Field()
  away_goals_ht = scrapy.Field()
  away_attemps = scrapy.Field()
  away_missed = scrapy.Field()
  away_freekicks = scrapy.Field()
  away_corners = scrapy.Field()
  away_offsite = scrapy.Field()
  away_fouls = scrapy.Field()
  away_held = scrapy.Field()
  away_possesion = scrapy.Field()
  away_passes = scrapy.Field()
  away_rating = scrapy.Field()
  away_tackles = scrapy.Field()
  away_yellow = scrapy.Field()
  away_red = scrapy.Field()
  away_players = scrapy.Field()
  away_tactic = scrapy.Field()


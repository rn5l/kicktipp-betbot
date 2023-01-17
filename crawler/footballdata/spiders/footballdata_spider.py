import scrapy

from crawler.footballdata.items import Data

class FootballdataSpider(scrapy.Spider):
    name = "footballdata"

    BASE_URL = 'https://www.football-data.co.uk/'
    LEAGUES = ['bundesliga','2liga','frankreich','england','italien','spanien']
    KEYS = ['D1','D2','F1','E0','I1','SP1']
    START_YEAR = 2017
    END_YEAR = 2023

    def start_requests(self):
        for item in zip( self.LEAGUES, self.KEYS ):
            for year in range( self.START_YEAR, self.END_YEAR + 1 ):
                league = item[0]
                key = item[1]
                year_prev = year - 1
                season_short = str(year_prev)[2:] + str(year)[2:]
                # https://www.football-data.co.uk/mmz4281/2122/F1.csv
                url = f'{self.BASE_URL}mmz4281/{season_short}/{key}.csv'
                req = scrapy.Request(url, self.parse_csv)
                req.meta['origin'] = self.name
                req.meta['league'] = league
                req.meta['year'] = year
                yield req

    def parse_csv(self, response):

        origin = response.meta['origin']
        league = response.meta['league']
        year = response.meta['year']

        data = Data()
        data['origin'] = origin
        data['year'] = year
        data['league_key'] = league
        data['raw'] = response.body.decode('utf-8')

        yield data

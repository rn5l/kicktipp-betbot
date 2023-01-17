import scrapy

from crawler.fussballdaten.items import Standings, Standing, Match

class FussballdatenSpider(scrapy.Spider):
    name = "fussballdaten"

    STATS_MAPPING = {
        'Ballbesitz (%)': 'possesion',
        'Schüsse aufs Tor': 'attemps',
        'Schüsse neben das Tor': 'missed',
        'Freistöße': 'freekicks',
        'Eckbälle': 'corners',
        'Abseits': 'offsite',
        'Gehaltene Bälle': 'held',
        'Fouls': 'fouls',
        'ø-Note': 'rating',
        'Zweikämpfe (%)': 'tackles',
        'Pässe (%)': 'passes',
        'Gelbe Karten': 'yellow',
        'Platzverweise': 'red'
    }

    BASE_URL = 'https://www.fussballdaten.de/'
    LEAGUES = ['bundesliga','2liga','frankreich','england','italien','spanien']
    START_YEAR = 2023
    END_YEAR = 2023

    def start_requests(self):
        league = 'england'
        year = 2021
        url = f'https://www.fussballdaten.de/bundesliga/2017/1/bmuenchen-bremen/'
        url = f'https://www.fussballdaten.de/england/2021/38/westham-southampton/'
        req = scrapy.Request(url, self.parse_match)
        req.meta['origin'] = self.name
        req.meta['league'] = league
        req.meta['year'] = year
        yield req

    def start_requests(self):
        for item in self.LEAGUES:
            for year in range( self.START_YEAR, self.END_YEAR + 1 ):
                league = item
                url = f'{self.BASE_URL}{league}/{year}/1/'
                req = scrapy.Request(url, self.parse_matchday)
                req.meta['origin'] = self.name
                req.meta['league'] = league
                req.meta['year'] = year
                yield req

    def parse_matchday(self, response):

        origin = response.meta['origin']
        league = response.meta['league']
        year = response.meta['year']

        stands = Standings()
        stand_list = list()

        matchday = response.url.split('/')[5]

        for row in response.css( 'div.content-tabelle table tbody tr' ):

            stand = Standing()

            stand['origin'] = origin
            stand['year'] = year
            stand['league_key'] = league

            stand['season'] = f'{year-1}/{year}'
            stand['league_name'] = response.css('ul#navi-header li:nth-child(1) a::text').get().strip()

            #stand['matchday'] = row.css('td:nth-child(4)::text').get()
            stand['matchday'] = matchday
            stand['place'] = row.css('td:nth-child(2)::text').get()

            href = row.css('td:nth-child(3) a::attr(href)').get()
            name = row.css('td:nth-child(3) a::text').get()
            stand['team_key'] = href.split('/')[2]
            stand['team_name'] = name.strip()

            stand['points'] = row.css('td:nth-child(6)::text').get()
            goals = row.css('td:nth-child(5)::text').get().strip().split(':')
            stand['goals'] = goals[0]
            stand['against'] = goals[1]

            stand_list.append( stand )

        stands['standings'] = stand_list
        yield stands

        matches = response.css('div.spiele-row')

        matches_complete = False
        for match in matches:
            finished = match.css( 'a.ergebnis' )

            info = match.css( 'span.wertung-info::text' )
            canceled = info and info.get() == 'abgesagt'

            if finished and not canceled:
                link = match.css('a.ergebnis::attr(href)').get()[1:]
                url = f'{self.BASE_URL}{link}'
                req = scrapy.Request(url, self.parse_match)
                req.meta['origin'] = self.name
                req.meta['league'] = league
                req.meta['year'] = year
                yield req
                matches_complete = True

        next_link = response.css('div.prevnext a.mr10')
        if next_link and matches_complete:
            link = response.css('div.prevnext a.mr10::attr(href)').get()[1:]
            url = f'{self.BASE_URL}{link}'
            req = scrapy.Request(url, self.parse_matchday)
            req.meta['origin'] = self.name
            req.meta['league'] = league
            req.meta['year'] = year
            yield req

    def parse_match(self, response):
        origin = response.meta['origin']
        league = response.meta['league']
        year = response.meta['year']

        match = Match()

        match['origin'] = origin
        match['year'] = year
        match['league_key'] = league
        match['season'] = f'{year-1}/{year}'

        matchday = response.url.split('/')[5]
        match['matchday'] = matchday

        match['link'] = response.url

        match['league_name'] = response.css('ul#navi-header li:nth-child(2) a::text').get().strip()

        infos = (''.join( response.css('div.ergebnis-info span::text').extract())).split('-')
        match['date'] = infos[2].split(',')[1].strip()

        home_club_div = response.css('div.box-spiel-verein.home')
        away_club_div = response.css('div.box-spiel-verein.away')

        home_key, home_name, home_short = self.get_club_info(home_club_div)
        away_key, away_name, away_short = self.get_club_info(away_club_div)

        match['home_key'] = home_key
        match['home_name'] = home_name
        match['home_short'] = home_short

        match['away_key'] = away_key
        match['away_name'] = away_name
        match['away_short'] = away_short

        result = response.css('div.box-spiel-ergebnis b::text').get()
        result_ht = response.css('div.ergebnis-info b::text').get()

        match['home_goals'] = result.split(':')[0]
        match['away_goals'] = result.split(':')[1]

        result_ht = result_ht.split('-')[1].strip()
        match['home_goals_ht'] = result_ht.split(':')[0].strip()
        match['away_goals_ht'] = result_ht.split(':')[1].strip()

        for stat in response.css('div.statistik-reihe'):
            stat_name = stat.css('div.text-center::text').get().strip()
            if stat_name in self.STATS_MAPPING:
                stat_key = self.STATS_MAPPING[stat_name]

                home_stat = stat.css('div:nth-child(1) span::text').get()
                away_stat = stat.css('div:nth-child(3) span::text').get()

                if home_stat:
                    match[f'home_{stat_key}'] = float(home_stat.replace(',','.'))
                if away_stat:
                    match[f'away_{stat_key}'] = float(away_stat.replace(',','.'))

        players = response.css('div.box.bs.green-top.p20 div.mt10.fs13 a.text::attr(href)').extract()
        players = list(map(lambda x: x.split('/')[2], players))

        match['home_players'] = ','.join( players[:11] )
        match['away_players'] = ','.join( players[11:] )

        url = response.url + 'aufstellung/'
        req = scrapy.Request(url, self.parse_tactics)
        req.meta['match'] = match
        yield req

    def get_club_info(self, div):
        href = div.css('a.text::attr(href)').get()
        key = href.split('/')[2]
        names = div.css('a.text span::text').extract()
        name = names[0].strip()
        short = names[1].strip()

        return key, name, short

    def parse_tactics(self, response):
        match = response.meta['match']

        home_tactics = response.css('p.box-spiel-titel b::text').get()
        away_tactics = response.css('p.box-spiel-titel.gast b::text').get()

        match['home_tactic'] = home_tactics
        match['away_tactic'] = away_tactics

        yield match

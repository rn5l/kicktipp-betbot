from pathlib import Path
from fuzzywuzzy import process
import pandas as pd
import json

BASE_DIR = '../data/'

def merge():

    footballdata = load_footballdata()
    fussballdaten = load_fussballdaten()

    merge_on = ['league_key','year','home_key','away_key']
    alldata = fussballdaten.merge( footballdata, on=merge_on, how='left' )

    filtered = filter(alldata)
    filtered.to_csv( f'{BASE_DIR}merged.csv', index=False )

    return

def filter(data):
    mando = [
        'league_key', 'league_name', 'year', 'season', 'matchday', 'date', 'home_key', 'away_key', 'link'
    ]

    keep_footballdata = [
        'Date', 'Time',
        'FTHG', 'FTAG', 'HTHG', 'HTAG', 
        'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR',
        'B365H', 'B365D', 'B365A', 'AvgH', 'AvgD', 'AvgA'
    ]

    rename_footballdata = [
        'Date', 'Time',
        'home_FTG', 'away_FTG', 'home_HTG', 'away_HTG', 
        'home_S', 'away_S', 'home_ST', 'away_ST', 'home_F', 'away_F', 'home_C', 'away_C', 'home_Y', 'away_Y', 'home_R', 'away_R',
        'home_B365', 'draw_B365', 'away_B365', 'home_Avg', 'draw_Avg', 'away_Avg'
    ]

    keep_fussballdaten = [
        'home_name', 'home_short', 'away_name', 'away_short', 'home_goals', 'away_goals', 'home_goals_ht',
        'away_goals_ht', 'home_possesion', 'away_possesion', 'home_attemps', 'away_attemps', 'home_missed',
        'away_missed', 'home_offsite', 'away_offsite', 'home_held', 'away_held', 'home_fouls', 'away_fouls',
        'home_passes', 'away_passes', 'home_yellow', 'away_yellow', 'home_red', 'away_red', 'home_players',
        'away_players', 'home_tactic', 'away_tactic', 'home_freekicks', 'away_freekicks', 'home_corners',
        'away_corners', 'home_rating', 'away_rating', 'home_tackles', 'away_tackles', 'home_st_place', 'home_st_points',
        'home_st_goals', 'home_st_against', 'away_st_place', 'away_st_points', 'away_st_goals', 'away_st_against'
    ]

    filtered = data[mando + keep_fussballdaten + keep_footballdata].sort_values( ['league_key','year','matchday'] )
    filtered.columns = mando + keep_fussballdaten + rename_footballdata
    return filtered

def load_footballdata():
    footballdata = pd.read_csv(f'{BASE_DIR}footballdata.csv')
    mapping = pd.read_csv(f'{BASE_DIR}mapping.csv', index_col=0)

    home_map = mapping[['footballdata', 'fussballdaten_key']].rename(columns={'fussballdaten_key': 'home_key'})
    footballdata_mapped = footballdata.merge(home_map, left_on='HomeTeam', right_on='footballdata', how='left').drop(
        'footballdata', 1)

    away_map = home_map.rename(columns={'home_key': 'away_key'})
    footballdata_mapped = footballdata_mapped.merge(away_map, left_on='AwayTeam', right_on='footballdata',
                                                    how='left').drop('footballdata', 1)

    return footballdata_mapped[ ~footballdata_mapped.home_key.isnull() & ~footballdata_mapped.away_key.isnull() ]


def load_fussballdaten():
    fussballdaten = pd.read_csv(f'{BASE_DIR}fussballdaten_matches.csv')
    standings = pd.read_csv(f'{BASE_DIR}fussballdaten_standings.csv')

    standings_relevant = standings[['team_key','year','matchday','place','points','goals','against']]
    standings_relevant.columns = ['home_key', 'year', 'matchday', 'home_st_place', 'home_st_points', 'home_st_goals',
                                  'home_st_against']
    fussballdaten_merged = fussballdaten.merge(standings_relevant, left_on=['home_key', 'year', 'matchday'],
                                               right_on=['home_key', 'year', 'matchday'], how='left')

    standings_relevant.columns = ['away_key', 'year', 'matchday', 'away_st_place', 'away_st_points', 'away_st_goals',
                                  'away_st_against']
    fussballdaten_merged = fussballdaten_merged.merge(standings_relevant, left_on=['away_key', 'year', 'matchday'],
                                               right_on=['away_key', 'year', 'matchday'], how='left')

    return fussballdaten_merged[ ~fussballdaten_merged.home_st_place.isnull() & ~fussballdaten_merged.away_st_place.isnull() ]

if __name__ == '__main__':
    merge()
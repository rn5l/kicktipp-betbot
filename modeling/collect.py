from pathlib import Path
import pandas as pd
import json

BASE_DIR = '../data/'

def collect():
    collect_fussballdaten()
    collect_footballdata()

def collect_fussballdaten():
    dir = f'{BASE_DIR}fussballdaten/'
    files = list(Path(dir).rglob('*.json'))

    standings = list()
    matches = list()

    for f in files:
        print(f.name)
        if f.name == 'standings.json':
            standings.append( get_standing_df(f) )
        else:
            matches.append( get_match_df(f) )

    all_standings = pd.concat(standings)
    all_standings.to_csv(f'{BASE_DIR}fussballdaten_standings.csv', index=False)

    all_matches = pd.concat(matches)
    all_matches.to_csv(f'{BASE_DIR}fussballdaten_matches.csv', index=False)

def get_standing_df(file):
    fileh = open(file)
    data = json.load(fileh)
    df = pd.DataFrame(data['standings'])

    return df

def get_match_df(file):
    fileh = open(file)
    data = json.load(fileh)
    df = pd.DataFrame([data])

    return df

def collect_footballdata():
    dir = f'{BASE_DIR}footballdata/'
    files = list(Path(dir).rglob('*.csv'))

    frames = []

    for f in files:
        print(f.name)
        frames.append( get_odds_df(f) )

    all = pd.concat( frames )
    all.to_csv( f'{BASE_DIR}footballdata.csv' )

def get_odds_df(file):
    parts = str(file).split('/')
    df = pd.read_csv(file)
    df['origin'] = parts[-4]
    df['league_key'] = parts[-3]
    df['year'] = parts[-2]

    return df

if __name__ == '__main__':
    collect()
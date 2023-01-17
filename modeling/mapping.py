from pathlib import Path
from fuzzywuzzy import process
import pandas as pd
import json

BASE_DIR = '../data/'

def mapping():
    footballdata = pd.read_csv(f'{BASE_DIR}footballdata.csv')
    fussballdaten = pd.read_csv(f'{BASE_DIR}fussballdaten_matches.csv')

    footballdata_home = list(footballdata['HomeTeam'].unique())
    fussballdaten_home = list(fussballdaten['home_short'].unique())

    key = []
    value = []
    match = []

    for club in fussballdaten_home:
        ratios = process.extract(club, footballdata_home)
        highest = process.extractOne(club, footballdata_home)
        key.append( club )
        value.append(highest[0])
        match.append(highest[1])
        print(f'{club} zu {highest}')

    mapping_df = pd.DataFrame()
    mapping_df['fussballdaten'] = key
    mapping_df['footballdata'] = value

    keys = pd.Series(index=fussballdaten['home_short'].values, data=fussballdaten['home_key'].values)
    key_map = keys.drop_duplicates(keep='first')
    mapping_df['fussballdaten_key'] = mapping_df['fussballdaten'].map( key_map )

    mapping_df.to_csv( f'{BASE_DIR}mapping.csv' )

    check_df = pd.DataFrame()
    check_df['TeamName'] = footballdata_home
    check_df.to_csv(f'{BASE_DIR}footballdata_teams.csv')

    #errors
    # Köln
    # Fürth
    # Nizza
    # La Coruna
    # Atalanta
    # Fiorentina
    # chievo
    # sampadoria

    return mapping_df

if __name__ == '__main__':
    mapping()
import pandas as pd

from modeling.models.lgbm.lgbm_goals import LgbmGoals
from modeling.models.lgbm.lgbm_multiclass import LgbmMulticlass
from modeling.models.simple.perfect import Perfect
from modeling.models.simple.simple_odds import SimpleOdds
from modeling.models.simple.simple_two_one import SimpleTwoOne

BASE_DIR = '../data/'

TEST_LEAGUE = 'bundesliga'
TEST_YEAR= 2022

MODELS = {
    'twoone': SimpleTwoOne(),
    'odds': SimpleOdds(),
    'lgb_class': LgbmMulticlass(),
    'lgb_goals': LgbmGoals(),
    'max': Perfect()
}

def experiment():

    data = load_data()
    data = data[data.home==1]

    match_league = data.league_key == TEST_LEAGUE
    match_year = data.year == TEST_YEAR
    test = data[match_league & match_year]
    train = data[~match_league | ~match_year]

    models = get_models()

    for key, model in models.items():
        model.train( train )

    out = [
        'matchday',
        'ta_key',
        'tb_key',
        'ta_odds',
        'draw_odds',
        'tb_odds',
        'ta_goals',
        'tb_goals',
    ]

    for key, model in models.items():
        goals_array = model.predict( test )
        cols = [f'{key}_goals_home',f'{key}_goals_away']
        test[cols] = goals_array
        out += cols

    res = []
    for key, model in models.items():
        res.append( evaluate(test, key) )

    print( pd.concat(res) )
    test[out].to_csv( f'{BASE_DIR}debug.csv', index=False)

    return

def evaluate(test, key):

    test['points_3'] = 0
    test['points_4'] = 0

    real_diff = test['ta_goals'] - test['tb_goals']
    real_diff_abs = real_diff.abs()
    real_draw = real_diff_abs == 0
    real_home = real_diff > 0
    real_away = real_diff < 0

    pred_diff = test[f'{key}_goals_home'] - test[f'{key}_goals_away']
    pred_diff_abs = pred_diff.abs()
    pred_draw = pred_diff_abs == 0
    pred_home = pred_diff > 0
    pred_away = pred_diff < 0

    base = (pred_home & real_home) | (pred_draw & real_draw) | (pred_away & real_away)
    diff = real_diff == pred_diff
    diff_no_draw = (real_diff == pred_diff) & ~real_draw
    exact = diff & (test[f'{key}_goals_home'] == test['ta_goals'])

    test.loc[base, 'points_3'] = test[base]['points_3'] + 1
    test.loc[diff, 'points_3'] = test[diff]['points_3'] + 1
    test.loc[exact, 'points_3'] = test[exact]['points_3'] + 1

    test.loc[base, 'points_4'] = test[base]['points_4'] + 2
    test.loc[diff_no_draw, 'points_4'] = test[diff_no_draw]['points_4'] + 1
    test.loc[exact, 'points_4'] = test[exact]['points_4'] + 1
    test.loc[exact & pred_draw & real_draw, 'points_4'] = test[exact & pred_draw & real_draw]['points_4'] + 1

    res = pd.DataFrame()
    res['key'] = [key]
    res['matches'] = len(test)
    res['points3'] = test['points_3'].sum()
    res['points4'] = test['points_4'].sum()

    return res

def get_models():
    return MODELS

def load_data():
    data = pd.read_csv(f'{BASE_DIR}prepared.csv')
    return data

if __name__ == '__main__':
    experiment()
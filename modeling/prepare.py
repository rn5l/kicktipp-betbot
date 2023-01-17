import pandas as pd
import numpy as np

BASE_DIR = '../data/'

def prepare():

    data = load_data()
    data['game_id'] = data.index + 1

    data_normal = data.copy()
    data_normal['home'] = 1

    data_reverse = data.copy()
    data_reverse['home'] = 0

    data_normal.columns = map(rename, list(data_normal.columns))
    data_reverse.columns = map(rename_rev, list(data_reverse.columns))

    combined = pd.concat([data_normal, data_reverse]).\
                    sort_values(['league_key', 'year', 'ta_key', 'matchday']).reset_index(drop=True)
    combined['result'] = (combined['ta_goals'] - combined['tb_goals']).clip(lower=-1, upper=1)
    combined['result_label'] = combined['result'] + 1

    features_ta = features(combined)
    features_tb = features_ta.copy()
    features_tb.columns = map(lambda x: x.replace('ta_', 'tb_'), features_tb.columns)

    full_df = combined.merge(features_ta, on=['league_key', 'year', 'matchday', 'ta_key'])
    full_df = full_df.merge(features_tb, on=['league_key', 'year', 'matchday', 'tb_key'])

    full_df.to_csv(f'{BASE_DIR}prepared.csv')

    return

def features(df):

    df['ta_result'] = df['result']
    df['ta_win'] = (df['ta_result'] > 0).astype(int)
    df['ta_draw'] = (df['ta_result'] == 0).astype(int)
    df['ta_points'] = (df['ta_win'] * 3) + (df['ta_draw'] * 1)
    df['ta_loss'] = (df['ta_result'] == -1).astype(int)

    df['ta_odds'] = df['ta_Avg']
    df.loc[df['ta_Avg'].isnull(), 'ta_odds'] = df[df['ta_Avg'].isnull()]['ta_B365']

    df['tb_odds'] = df['tb_Avg']
    df.loc[df['tb_Avg'].isnull(), 'tb_odds'] = df[df['tb_Avg'].isnull()]['tb_B365']

    df['draw_odds'] = df['draw_Avg']
    df.loc[df['draw_Avg'].isnull(), 'draw_odds'] = df[df['draw_Avg'].isnull()]['draw_B365']

    stf = standing_features(df)
    lmf = last_matches_features(df)
    emf = expanding_matches_features(df)

    features = df[['league_key', 'year', 'matchday', 'ta_key']]
    features = features.merge(stf, left_index=True, right_index=True)
    features = features.merge(lmf, left_index=True, right_index=True)
    features = features.merge(emf, left_index=True, right_index=True)

    return features


def standing_features(df):
    shift = ['ta_st_place','ta_st_points','ta_st_goals','ta_st_against']
    features = pd.DataFrame()
    group = df.groupby( ['league_key','year','ta_key'] )
    for col in shift:
        features[f'{col}_prev'] = group[col].shift()
    features[f'matchday_prev'] = group['matchday'].shift()
    for col in shift:
        features[f'{col}_prev_ratio'] = features[f'{col}_prev'] / features[f'matchday_prev']
    return features

def last_matches_features(df, windows=5, min_periods=3, closed='left'):

    features = pd.DataFrame()
    group = df.groupby( ['league_key','year','ta_key'] )

    #features[f'ta_goals_avg'] = group['ta_goals'].rolling( windows, min_periods=min_periods, closed='left').mean()
    features[f'ta_lm_goals_avg'] = group['ta_goals'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).mean())
    features[f'ta_lm_result_avg'] = group['ta_result'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).mean())
    features[f'ta_lm_win_avg'] = group['ta_win'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).mean())
    features[f'ta_lm_points_avg'] = group['ta_win'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).mean())
    features[f'ta_lm_odds_avg'] = group['ta_odds'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).mean())

    features[f'ta_lm_goals_wavg'] = group['ta_goals'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).apply(wma_exp))
    features[f'ta_lm_result_wavg'] = group['ta_result'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).apply(wma_exp))
    features[f'ta_lm_win_wavg'] = group['ta_win'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).apply(wma_exp))
    features[f'ta_lm_points_wavg'] = group['ta_points'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).apply(wma_exp))
    features[f'ta_lm_odds_wavg'] = group['ta_odds'].transform(lambda s: s.rolling(windows, min_periods=min_periods, closed=closed).apply(wma_exp))

    return features

def expanding_matches_features(df, min_periods=3, closed='left'):
    features = pd.DataFrame()
    group = df.groupby( ['league_key','year','ta_key'] )

    #features[f'ta_goals_avg'] = group['ta_goals'].rolling( windows, min_periods=min_periods, closed='left').mean()
    features[f'ta_em_count'] = group['ta_goals'].transform(lambda s: s.expanding(min_periods=min_periods).count().shift())
    features[f'ta_em_goals_avg'] = group['ta_goals'].transform(lambda s: s.expanding(min_periods=min_periods).mean().shift())
    features[f'ta_em_result_avg'] = group['ta_result'].transform(lambda s: s.expanding(min_periods=min_periods).mean().shift())
    features[f'ta_em_win_avg'] = group['ta_win'].transform(lambda s: s.expanding(min_periods=min_periods).mean().shift())
    features[f'ta_em_draw_avg'] = group['ta_draw'].transform(lambda s: s.expanding(min_periods=min_periods).mean().shift())
    features[f'ta_em_points_avg'] = group['ta_win'].transform(lambda s: s.expanding(min_periods=min_periods).mean().shift())

    return features

def wma_exp(seq):
    exp = np.flip( np.ones( seq.shape[0] ) / np.arange(1,seq.shape[0]+1) )
    return np.sum(seq * exp) / np.sum(exp)

def rename(column):
    res = column.replace('home_', 'ta_')
    res = res.replace('away_', 'tb_')
    return res

def rename_rev(column):
    res = column.replace('home_', 'tb_')
    res = res.replace('away_', 'ta_')
    return res

def load_data():
    data = pd.read_csv(f'{BASE_DIR}merged.csv')
    return data

if __name__ == '__main__':
    prepare()
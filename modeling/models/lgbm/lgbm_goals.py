from sklearn.model_selection import train_test_split

from modeling.models.lgbm.features import FEATURES_ST, FEATURES_LM, FEATURES_EM, FEATURES_DIRECT
from modeling.models.model import Model
from modeling.models.simple.simple_odds import SimpleOdds

import numpy as np
import lightgbm as lgbm

class LgbmGoals(Model):

    backup = None
    models_home = []
    models_away = []
    models_diff = []

    def __init__(self):
        self.backup = SimpleOdds()
        self.num_models = 5
        pass

    def train(self, training_data):
        self.backup.train( training_data )

        FEATURES_TA = FEATURES_ST + FEATURES_LM + FEATURES_EM
        FEATURES_TB = list(map(lambda x: x.replace('ta_','tb_'), FEATURES_TA))
        self.FEATURES = FEATURES_DIRECT + FEATURES_TA + FEATURES_TB

        MAX_EPOCHS = 5000
        STOPPING = 100

        params = {}
        params['boosting'] = 'gbdt'
        params['learning_rate'] = 0.1
        params['application'] = 'regression'
        params['num_classes'] = 1
        # params['metric'] = 'binary_logloss'
        params['max_depth'] = -1
        # params['num_leaves'] = 64
        # params['max_bin'] = 512
        params['feature_fraction'] = 0.5
        params['bagging_fraction'] = 0.5
        params['min_data_in_leaf'] = 5
        # params['verbosity'] = 0

        # ensure_dir( BASE_PATH + SET + 'lgbm/' )
        # model.save_model( BASE_PATH + SET + 'lgbm/'+ALGKEY+'.'+str(i)+'.txt' , num_iteration=model.best_iteration, )

        TARGET_HOME = 'ta_goals'
        TARGET_AWAY = 'tb_goals'
        TARGET_DIFF = 'ta_goals_diff'

        training_data['ta_goals_diff'] = training_data['ta_goals'] - training_data['tb_goals']

        for n in range(self.num_models):

            train_tr, train_val = train_test_split(training_data, test_size=0.2)

            d_train = lgbm.Dataset(train_tr[self.FEATURES], label=train_tr[TARGET_HOME],
                                   feature_name=self.FEATURES)  # + ['session_id'])#, categorical_feature=CAT_FEATURES )
            d_valid = lgbm.Dataset(train_val[self.FEATURES], label=train_val[TARGET_HOME],
                                   feature_name=self.FEATURES)  # + ['session_id'])#, categorical_feature=CAT_FEATURES )
            watchlist = (d_train, d_valid)
            evals_result = {}
            model = lgbm.train(params, train_set=d_train, num_boost_round=MAX_EPOCHS, valid_sets=watchlist,
                               early_stopping_rounds=STOPPING, evals_result=evals_result, verbose_eval=10)
            self.models_home.append(model)

            d_train = lgbm.Dataset(train_tr[self.FEATURES], label=train_tr[TARGET_AWAY],
                                   feature_name=self.FEATURES)  # + ['session_id'])#, categorical_feature=CAT_FEATURES )
            d_valid = lgbm.Dataset(train_val[self.FEATURES], label=train_val[TARGET_AWAY],
                                   feature_name=self.FEATURES)  # + ['session_id'])#, categorical_feature=CAT_FEATURES )
            watchlist = (d_train, d_valid)
            evals_result = {}
            model = lgbm.train(params, train_set=d_train, num_boost_round=MAX_EPOCHS, valid_sets=watchlist,
                               early_stopping_rounds=STOPPING, evals_result=evals_result, verbose_eval=10)
            self.models_away.append(model)

            d_train = lgbm.Dataset(train_tr[self.FEATURES], label=train_tr[TARGET_DIFF],
                                   feature_name=self.FEATURES)  # + ['session_id'])#, categorical_feature=CAT_FEATURES )
            d_valid = lgbm.Dataset(train_val[self.FEATURES], label=train_val[TARGET_DIFF],
                                   feature_name=self.FEATURES)  # + ['session_id'])#, categorical_feature=CAT_FEATURES )
            watchlist = (d_train, d_valid)
            evals_result = {}
            model = lgbm.train(params, train_set=d_train, num_boost_round=MAX_EPOCHS, valid_sets=watchlist,
                               early_stopping_rounds=STOPPING, evals_result=evals_result, verbose_eval=10)
            self.models_diff.append(model)

    def predict(self, test_data):

        test_data['tmp_goals_home'] = 0
        test_data['tmp_goals_away'] = 0
        test_data['tmp_goals_diff'] = 0
        test_data['tmp_home'] = False

        fallback = test_data['ta_lm_goals_avg'].isnull()

        res_back = self.backup.predict( test_data[fallback] )
        test_data.loc[ fallback, 'tmp_goals_home' ] = res_back.T[0]
        test_data.loc[fallback, 'tmp_goals_away'] = res_back.T[1]

        X_test = test_data[~fallback][self.FEATURES].values.astype(np.float32)

        goals_home = None
        goals_away  = None
        goals_diff = None
        for n in range(self.num_models):
            gh_pred = self.models_home[n].predict(X_test, num_iteration=self.models_home[n].best_iteration)
            ga_pred = self.models_away[n].predict(X_test, num_iteration=self.models_away[n].best_iteration)
            gd_pred = self.models_diff[n].predict(X_test, num_iteration=self.models_diff[n].best_iteration)

            goals_home = gh_pred if goals_home is None else goals_home + gh_pred
            goals_away = ga_pred if goals_away is None else goals_away + ga_pred
            goals_diff = gd_pred if goals_diff is None else goals_diff + gd_pred

        goals_home = goals_home / self.num_models
        goals_away = goals_away / self.num_models
        goals_diff = goals_diff / self.num_models

        home = goals_diff > 0
        test_data.loc[~fallback, 'tmp_home'] = home

        test_data.loc[~fallback, 'tmp_goals_home'] = np.round(goals_home)
        test_data.loc[~fallback, 'tmp_goals_away'] = np.round(goals_away)

        home = test_data.tmp_home
        test_data.loc[~fallback & home, 'tmp_goals_home'] = test_data[~fallback & home]['tmp_goals_home'] + 1
        test_data.loc[~fallback & ~home, 'tmp_goals_away'] = test_data[~fallback & ~home]['tmp_goals_away'] + 1

        return test_data[['tmp_goals_home','tmp_goals_away']].values
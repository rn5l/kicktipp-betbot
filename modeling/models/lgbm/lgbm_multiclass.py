from sklearn.model_selection import train_test_split

from modeling.models.lgbm.features import FEATURES_ST, FEATURES_LM, FEATURES_EM, FEATURES_DIRECT
from modeling.models.model import Model
from modeling.models.simple.simple_odds import SimpleOdds

import numpy as np
import lightgbm as lgbm

class LgbmMulticlass(Model):

    backup = None
    models = []

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
        params['application'] = 'multiclass'
        # params['metric'] = 'binary_logloss'
        #params['max_depth'] = -1
        # params['num_leaves'] = 64
        # params['max_bin'] = 512
        params['feature_fraction'] = 0.5
        params['bagging_fraction'] = 0.5
        params['min_data_in_leaf'] = 5
        # params['verbosity'] = 0

        # ensure_dir( BASE_PATH + SET + 'lgbm/' )
        # model.save_model( BASE_PATH + SET + 'lgbm/'+ALGKEY+'.'+str(i)+'.txt' , num_iteration=model.best_iteration, )

        TARGET = 'result_label'

        params['application'] = 'multiclass'
        params['num_classes'] = 3

        for n in range(self.num_models):

            train_tr, train_val = train_test_split(training_data, test_size=0.2)

            d_train = lgbm.Dataset(train_tr[self.FEATURES], label=train_tr[TARGET],
                                   feature_name=self.FEATURES)  # + ['session_id'])#, categorical_feature=CAT_FEATURES )
            d_valid = lgbm.Dataset(train_val[self.FEATURES], label=train_val[TARGET],
                                   feature_name=self.FEATURES)  # + ['session_id'])#, categorical_feature=CAT_FEATURES )

            watchlist = (d_train, d_valid)
            evals_result = {}

            model = lgbm.train(params, train_set=d_train, num_boost_round=MAX_EPOCHS, valid_sets=watchlist,
                               early_stopping_rounds=STOPPING, evals_result=evals_result, verbose_eval=10)
            self.models.append(model)

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

        y_prob = None
        for n in range(self.num_models):
            pred = self.models[n].predict(X_test, num_iteration=self.models[n].best_iteration).T
            y_prob = pred if y_prob is None else y_prob + pred

        y_prob = y_prob / self.num_models

        diff = y_prob[0] - y_prob[2]
        diff_abs = np.abs(diff)
        home = diff < 0

        test_data.loc[~fallback, 'tmp_diff_abs'] = diff_abs
        test_data.loc[~fallback, 'tmp_home'] = home

        test_data.loc[~fallback & (test_data.tmp_diff_abs > 0.02), 'tmp_goals_diff'] = 1
        test_data.loc[~fallback & (test_data.tmp_diff_abs > 0.3), 'tmp_goals_diff'] = 2
        test_data.loc[~fallback & (test_data.tmp_diff_abs > 0.6), 'tmp_goals_diff'] = 3

        test_data.loc[~fallback, 'tmp_goals_home'] = np.round( y_prob[2]**3 * 5 )
        test_data.loc[~fallback, 'tmp_goals_away'] = np.round( y_prob[0]**3 * 5 )

        test_data.loc[~fallback, 'tmp_goals_home'] = 1
        test_data.loc[~fallback, 'tmp_goals_away'] = 1

        home = test_data.tmp_home
        test_data.loc[~fallback & home, 'tmp_goals_home'] = 1 + test_data[~fallback & home]['tmp_goals_diff']
        test_data.loc[~fallback & ~home, 'tmp_goals_away'] = 1 + test_data[~fallback & ~home]['tmp_goals_diff']

        return test_data[['tmp_goals_home','tmp_goals_away']].values
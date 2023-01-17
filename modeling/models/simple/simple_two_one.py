from modeling.models.model import Model
import numpy as np

class SimpleTwoOne(Model):

    def __init__(self):
        pass

    def train(self, training_data):
        print('nothing to do')
        return

    def predict(self, test_data):

        home_wins = test_data['ta_odds'] < test_data['tb_odds']

        goals = np.ones(len(test_data)) + 1
        goals2 = np.ones(len(test_data))

        goals_home = np.where(home_wins, goals, goals2)
        goals_away = np.where(home_wins, goals2, goals)

        return np.stack( (goals_home,goals_away), axis=1 )

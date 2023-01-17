from modeling.models.model import Model
import numpy as np

class SimpleOdds(Model):

    def __init__(self, draw_thres=0.3, dom_thres=8):
        self.domination_threshold = dom_thres
        self.draw_threshold = draw_thres
        pass

    def train(self, training_data):
        print('nothing to do')
        return

    def predict(self, test_data):

        diff = (test_data['ta_odds'] - test_data['tb_odds']).abs()
        home_wins = test_data['ta_odds'] < test_data['tb_odds']

        draw = diff < self.draw_threshold
        dom = diff >= self.domination_threshold
        dom2 = diff >= self.domination_threshold / 2

        goals = np.ones(len(test_data))
        goals = np.where(~draw, goals+1, goals )
        goals = np.where(dom2, goals + 1, goals)
        goals = np.where(dom, goals + 1, goals)
        goals2 = np.ones(len(test_data))

        goals_home = np.where(home_wins, goals, goals2)
        goals_away = np.where(home_wins, goals2, goals)

        return np.stack( (goals_home,goals_away), axis=1 )

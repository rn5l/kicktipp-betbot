from modeling.models.model import Model
import numpy as np

class Perfect(Model):

    def __init__(self):
        pass

    def train(self, training_data):
        print('nothing to do')
        return

    def predict(self, test_data):
        return test_data[['ta_goals','tb_goals']].values

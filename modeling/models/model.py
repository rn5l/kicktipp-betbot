from abc import ABC, abstractmethod

class Model(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def train(self, training_data):
        pass

    @abstractmethod
    def predict(self, test_data):
        pass
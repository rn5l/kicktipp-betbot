"""
Simple preditor for kicktipp bet bot.
"""
from helper.match import Match
from .base import PredictorBase
import math


class SimplePredictor(PredictorBase):
    DOMINATION_THRESHOLD = 8
    DRAW_THRESHOLD = 0.3

    def predict(self, match: Match):

        diff = math.fabs(match.rate_home - match.rate_road)
        home_wins = match.rate_home < match.rate_road

        if diff < self.DRAW_THRESHOLD:
            return (1, 1)

        if diff >= self.DOMINATION_THRESHOLD:
            result = (4, 1)
        elif diff >= self.DOMINATION_THRESHOLD / 2:
            result = (3, 1)
        else:
            result = (2, 1)

        return result if home_wins else tuple(reversed(result))

from river import anomaly
from river import base

class SequenceModel(base.Estimator):
    def __init__(self,
                 models: list[anomaly.base.AnomalyDetector | anomaly.base.SupervisedAnomalyDetector],
                 y_key: str):
        self.models = models
        self.y_key = y_key

    @property
    def _supervised(self):
        return False

    def learn_one(self, x: dict, **params):
        inp_x = x
        inp_y = x[self.y_key]

        for m in self.models:
            score = 0
            if m._supervised:
                score = m.score_one(x={}, y=inp_y, **params)
                m.learn_one(x={}, y=inp_y, **params)
            else:
                score = m.score_one(inp_x, **params)
                m.learn_one(inp_x, **params)

            inp_x = {self.y_key: score}
            inp_y = score

    def score_one(self, x: dict, **params):
        inp_x = x
        inp_y = x[self.y_key]
        score = 0

        for m in self.models:
            if m._supervised:
                score = m.score_one(x={}, y=inp_y, **params)
            else:
                score = m.score_one(inp_x, **params)

            inp_x = {self.y_key: score}
            inp_y = score

        return score
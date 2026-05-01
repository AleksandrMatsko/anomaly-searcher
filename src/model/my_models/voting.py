from river import anomaly

class VotingAnomalyFilter(anomaly.base.AnomalyFilter):

    def __init__(self, 
                 models : list[anomaly.base.AnomalyFilter],
                 y_key: str,
                 ):
        self.models = models
        self.y_key = y_key

    @property
    def _supervised(self):
        return False

    def learn_one(self, x: dict, **params):
        for m in self.models:
            if m._supervised:
                m.learn_one(None, x[self.y_key], **params)
            else:
                m.learn_one(x, **params)

    def score_one(self, x: dict, **params):
        scores = []

        for m in self.models:
            if m._supervised:
                score = m.score_one(None, x[self.y_key])
            else:
                score = m.score_one(x)

            scores.append(score)

        if len(scores) == 0:
            return 0
        
        return sum(scores) / len(scores)
    
    def classify(self, score, **params) -> bool:
        x = params.get("my_x")
        y = x[self.y_key]

        is_anomaly = 0
        not_anomaly = 0

        for m in self.models:
            if m._supervised:
                score = m.score_one(None, x[self.y_key])
            else:
                score = m.score_one(x)

            if m.classify(score):
                is_anomaly += 1
            else:
                not_anomaly += 1

        return is_anomaly > not_anomaly

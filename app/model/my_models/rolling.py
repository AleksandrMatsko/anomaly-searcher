from collections.abc import Callable
from river import stats, anomaly
import math

__all__ = ["RollingModel"]

class RollingModel(anomaly.base.AnomalyDetector):
    def __init__(self, 
                 model_create_func : Callable[[dict], anomaly.base.AnomalyDetector],
                 model_params: dict,
                 num_models : int,
                 model_ttl : int,
                 time_shift : int,
                 agg_score_func : Callable[[list[float]], float],
                 ):
        self.model_create_func = model_create_func
        self.model_params = model_params
        self.num_models = num_models
        self.time_shift = time_shift

        self.__models = [self.model_create_func(self.model_params) for _ in range(num_models)]
        self.model_ttl = model_ttl
        self.__ttls = [-1 * i *time_shift for i in range(num_models)]
        
        self.agg_score_func = agg_score_func

    @property
    def _supervised(self):
        return False

    def learn_one(self, *args, **learn_kwargs) -> None:
        for idx, model in enumerate(self.__models):
            self.__ttls[idx] += 1
            if self.__ttls[idx] == self.model_ttl:
                self.__models[idx] = self.model_create_func(self.model_params)
                self.__ttls[idx] = 0
            elif self.__ttls[idx] >= 0:
                model.learn_one(*args, **learn_kwargs)

    def score_one(self, *args, **kwargs) -> float:
        scores = self.__get_scores(*args, **kwargs)

        sum_ttls = sum([v if v >= 0 else 0 for v in self.__ttls])
        if sum_ttls == 0:
            return self.agg_score_func(scores)

        return self.agg_score_func(scores) / sum_ttls

    def __get_scores(self, *args, **kwargs) -> list[float]:
        scores = []
        for idx, model in enumerate(self.__models):
            if self.__ttls[idx] >= 0:
                scores.append(
                    model.score_one(*args, **kwargs) * 
                    self.__ttls[idx])
        
        return scores
    
class RollingQuantileFilter(anomaly.base.AnomalyFilter):

    def __init__(self, 
                 anomaly_detector, 
                 q: float, 
                 window_size: int,
                 protect_anomaly_detector=True,
                 ):
        super().__init__(
            anomaly_detector=anomaly_detector,
            protect_anomaly_detector=protect_anomaly_detector,
        )
        self.q = q
        self.window_size = window_size
        self.quantile = stats.RollingQuantile(q=q, window_size=window_size)

    # @property
    # def q(self):
    #     return self.q
    
    # @property
    # def window_size(self):
    #     return self.window_size

    def classify(self, score):
        return score >= (self.quantile.get() or math.inf)
    
    def learn_one(self, *args, **learn_kwargs):
        score = self.score_one(*args)
        if not self.protect_anomaly_detector or not self.classify(score):
            self.anomaly_detector.learn_one(*args, **learn_kwargs)
        self.quantile.update(score)

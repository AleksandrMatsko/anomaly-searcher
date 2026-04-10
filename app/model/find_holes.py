import bisect

from app.metrics.metric import Metric

from .model import AnomalyDetectionModel, MODELS_DICT

class HolesFinderAnomalyDetectorWrapper(AnomalyDetectionModel):
    __last_observed_ts: int

    def __init__(self,
                 wrapped: AnomalyDetectionModel,
                 last_observed_ts: int = 0):
        self.__last_observed_ts = last_observed_ts
        self.__in_the_hole = False
        self.__wrapped = wrapped

    def predict_one(self, metric: Metric) -> bool:
        first_not_observed_ts_idx = bisect.bisect(
            metric.values, 
            self.__last_observed_ts, 
            key=lambda mv: mv.timestamp)
        
        if first_not_observed_ts_idx == len(metric.values):
            # all observations are in the past
            # we may be in the hole

            delta = metric.queried_at - self.__last_observed_ts
            if delta > 60:
                # delta is greater than minute
                # we are definetly in the hole
                self.__in_the_hole = True
                return True
            
            self.__in_the_hole = False
            return self.__wrapped.predict_one(metric)
        
        self.__last_observed_ts = metric.values[-1].timestamp
        self.__in_the_hole = False

        return self.__wrapped.predict_one(metric)
    
    @staticmethod
    def config_name() -> str:
        return "holes_finder_wrapper"

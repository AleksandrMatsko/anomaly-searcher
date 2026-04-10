import bisect

from app.metrics.metric import Metric

from .model import AnomalyDetectionModel, MODELS_DICT

class HolesFinderAnomalyDetector(AnomalyDetectionModel):
    __last_observed_ts: int

    def __init__(self,
                 last_observed_ts: int = 0):
        self.__last_observed_ts = last_observed_ts
        self.__in_the_hole = False

    def predict_one(self, metric: Metric) -> bool:
        print(f"metric: {metric.name} quaried_at {metric.queried_at}")
        print(f"values: {metric.values}")
        print(f"last_observed_ts = {self.__last_observed_ts}")

        first_not_observed_ts_idx = bisect.bisect(
            metric.values, 
            self.__last_observed_ts, 
            key=lambda mv: mv.timestamp)
        
        # TODO: understand
        # 1. if the hole started
        # 2. if the hole ended
        # 3. if in the middle of the hole
        
        if first_not_observed_ts_idx == len(metric.values):
            # all observations are in the past
            # we may be in the hole

            delta = metric.queried_at - self.__last_observed_ts
            if delta > 60:
                # delta is greater than minute
                # we are definetly in the hole
                self.__in_the_hole = True
                return True
            
            # TODO: what to do with the model ?
            self.__in_the_hole = False
            return False
        
        # TODO: score and learn anomaly detection model

        self.__last_observed_ts = metric.values[-1].timestamp
        self.__in_the_hole = False
        return False
    
    @staticmethod
    def config_name() -> str:
        return "holes_finder"
    
MODELS_DICT[HolesFinderAnomalyDetector.config_name()] = lambda params: HolesFinderAnomalyDetector(**params)
import bisect
from . import my_models as my_models

from app.metrics.metric import Metric
from .model import AnomalyDetectionModel, MODELS_DICT

import river.time_series as ts
import river.anomaly as anomaly

def create_ILOF(params: dict):
    return anomaly.LocalOutlierFactor(**params)

def average(l: list[float]) -> float:
    return sum(l) / len(l)

def create_RollingILOF(ilof_params: dict):
    return my_models.RollingModel(
        model_create_func=create_ILOF,
        model_params=ilof_params,
        num_models=5,
        model_ttl=100,
        time_shift=20,
        agg_score_func=average,
    )

class VotingOf3ModelsWith2Seq(AnomalyDetectionModel):
    def __init__(self,
                 last_observed_ts: int = 0,
                 ):
        self.__last_observed_ts = last_observed_ts
        self.NEED_TO_OBSERVE = 2
        self.__just_created = True        

    def predict_one(self, metric: Metric) -> bool:
        first_not_observed_ts_idx = bisect.bisect(
            metric.values, 
            self.__last_observed_ts, 
            key=lambda mv: mv.timestamp,
        )
        if self.__just_created:
            if len(metric.values) < self.NEED_TO_OBSERVE:
                return False
            
            first_not_observed_ts_idx = 0
            self.__just_created = False

            holt_winters = ts.HoltWinters(alpha=0.23)
            holt_winters.learn_one(x=None, y=metric.values[0].value)
            holt_winters.learn_one(x=None, y=metric.values[1].value)

            self.model = my_models.VotingAnomalyFilter(
                models=[
                    my_models.wrap_with_rolling_filter(my_models.SequenceModel(
                        models=[
                            create_RollingILOF({"n_neighbors": 7}),  
                            my_models.wrap_with_PDA(holt_winters),
                        ],
                        y_key="now-0"
                    ), True),
                    my_models.wrap_with_rolling_filter(my_models.SequenceModel(
                        models=[
                            create_RollingILOF({"n_neighbors": 7}),  
                            my_models.Autoencoder(
                                n_features=1,
                                hidden_size=1,
                                lr=0.1,
                            ),
                        ],
                        y_key="now-0"
                    ), True),
                    my_models.wrap_with_rolling_filter(my_models.Autoencoder(
                        n_features=1,
                        hidden_size=1,
                        lr=0.1,
                    ), False),
                ],
                y_key="now-0"
            )

        is_anomaly = False
        for i in range(first_not_observed_ts_idx, len(metric.values)):
            x = {
                "now-0": metric.values[i].value,
            }
            
            score = self.model.score_one(x)
            is_anomaly = self.model.classify(score, my_x=x)

            self.model.learn_one(x)

        self.__last_observed_ts = metric.values[-1].timestamp
        return is_anomaly
    
    @staticmethod
    def config_name() -> str:
        return "voting_of_3_models_with_2_seq"
    
    def model_type(self) -> str:
        return self.__class__.config_name()
    
MODELS_DICT[VotingOf3ModelsWith2Seq.config_name()] = lambda params: VotingOf3ModelsWith2Seq(**params)

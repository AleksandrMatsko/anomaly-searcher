from app.metrics.metric import Metric

from .model import AnomalyDetectionModel, MODELS_DICT

class DummyAnomalyDetector(AnomalyDetectionModel):
    """Tells that anomaly for anomaly_count times. When tells no anomaly for non_anomaly_count times."""
    __anomaly_count : int
    __non_anomaly_count : int
    __window_size : int
    __state : int

    def __init__(self, 
                 anomaly_count : int = 2,
                 non_anomaly_count : int = 10,
                 ):
        self.__anomaly_count = anomaly_count
        self.__non_anomaly_count = non_anomaly_count
        self.__window_size = self.__anomaly_count + self.__non_anomaly_count
        self.__state = 0

    def predict_one(self, metric: Metric) -> bool:
        print(f"dummy model got metric: {metric}")
        if self.__state < self.__anomaly_count:
            self.__state += 1
            return True
        
        self.__state = (self.__state + 1) % self.__window_size
        return False
    
    @staticmethod
    def config_name() -> str:
        return "dummy"
    
MODELS_DICT[DummyAnomalyDetector.config_name()] = lambda params: DummyAnomalyDetector(**params)
        
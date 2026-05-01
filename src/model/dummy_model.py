from src.metrics.metric import Metric

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
        if self.__state < self.__anomaly_count:
            self.__state += 1
            return True
        
        self.__state = (self.__state + 1) % self.__window_size
        return False
    
    @staticmethod
    def config_name() -> str:
        return "dummy"
    
    def model_type(self) -> str:
        return "dummy"
    
MODELS_DICT[DummyAnomalyDetector.config_name()] = lambda params: DummyAnomalyDetector(**params)

class AlwaysNonAnomalyDetector(AnomalyDetectionModel):
    """Always tell there is no anomaly"""
    def __init__(self):
        pass

    def predict_one(self, metric: Metric) -> bool:
        return False
    
    @staticmethod
    def config_name() -> str:
        return "always_non_anomaly"
    
    def model_type(self) -> str:
        return "always_non_anomaly"
    
MODELS_DICT[AlwaysNonAnomalyDetector.config_name()] = lambda params: AlwaysNonAnomalyDetector(**params)

class AlwaysAnomalyDetector(AnomalyDetectionModel):
    """Always tell there is anomaly"""
    def __init__(self):
        pass

    def predict_one(self, metric: Metric) -> bool:
        return True
    
    @staticmethod
    def config_name() -> str:
        return "always_anomaly"
    
    def model_type(self) -> str:
        return self.__class__.config_name()
    
MODELS_DICT[AlwaysAnomalyDetector.config_name()] = lambda params: AlwaysAnomalyDetector(**params)

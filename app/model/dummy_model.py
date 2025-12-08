import random

from app.metrics.metric import Metric

from .model import AnomalyDetectionModel

class DummyAnomalyDetector(AnomalyDetectionModel):
    """Randomly tells that datapoint is anomaly with probability chance / total_chances"""
    __chance : int
    __total_chances : int

    def __init__(self, 
                 chance : int = 1,
                 total_chances : int = 100,
                 ):
        self.__chance = chance
        self.__total_chances = total_chances

    def predict_one(self, metric: Metric) -> bool:
        return random.randint(0, self.__total_chances) <= self.__chance

import typing
from abc import ABC, abstractmethod

class AnomalyDetectionModel(ABC):

    @abstractmethod
    def predict_one(self, x : typing.Dict[str, object], y typing.Dict[str, object]):
        pass

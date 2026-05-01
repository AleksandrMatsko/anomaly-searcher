import pickle
import typing

from abc import ABC, abstractmethod

import src.metrics as metrics

MODELS_DICT: typing.Dict[str, typing.Callable]  = {}

class AnomalyDetectionModel(ABC):

    @abstractmethod
    def predict_one(self, metric : metrics.Metric) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def config_name() -> str:
        pass

    @abstractmethod
    def model_type(self) -> str:
        pass

def pickle_model(model : AnomalyDetectionModel) -> bytes:
    return pickle.dumps(model)

def unpickle_model(bytes : bytes) -> (AnomalyDetectionModel | None):
    if bytes is None:
        return None
    return pickle.loads(bytes) # type: ignore
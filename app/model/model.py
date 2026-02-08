import pickle
from abc import ABC, abstractmethod

import app.metrics as metrics

class AnomalyDetectionModel(ABC):

    @abstractmethod
    def predict_one(self, metric : metrics.Metric) -> bool:
        pass

def pickle_model(model : AnomalyDetectionModel) -> bytes:
    return pickle.dumps(model)

def unpickle_model(bytes : bytes) -> (AnomalyDetectionModel | None):
    if bytes is None:
        return None
    return pickle.loads(bytes) # type: ignore
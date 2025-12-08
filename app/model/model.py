import typing
from abc import ABC, abstractmethod

import app.metrics as metrics

class AnomalyDetectionModel(ABC):

    @abstractmethod
    def predict_one(self, metric : metrics.Metric):
        pass

from abc import ABC, abstractmethod

from app.model import AnomalyDetectionModel

class ModelStorage(ABC):
    @abstractmethod
    def save_model(self, key : str, model : AnomalyDetectionModel):
        pass
    
    @abstractmethod
    def get_model(self, key : str) -> (AnomalyDetectionModel | None):
        pass
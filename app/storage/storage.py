from abc import ABC, abstractmethod
from enum import StrEnum
from dataclasses import dataclass

from app.model import AnomalyDetectionModel
from app.alert import AlertInfo

class StorageType(StrEnum):
    UNKNOWN = ""
    IN_MEMORY = "IN_MEMORY"
    REDIS = "REDIS"

class ModelStorage(ABC):
    @abstractmethod
    def save_model(self, key : str, model : AnomalyDetectionModel):
        pass
    
    @abstractmethod
    def get_model(self, key : str) -> (AnomalyDetectionModel | None):
        pass

class AlertInfoStorage(ABC):
    @abstractmethod
    def save_alert_info(self, key : str, info : AlertInfo):
        pass

    @abstractmethod
    def get_alert_info(self, key : str) -> (AlertInfo | None):
        pass

class Storage(ModelStorage, AlertInfoStorage):
    pass
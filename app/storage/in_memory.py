from app.model.model import AnomalyDetectionModel
from app.alert import AlertInfo 

from .storage import *

class InMemoryStorage(ModelStorage, AlertInfoStorage):
    __kv_model_storage : dict
    __kv_alert_storage : dict

    def __init__(self):
        self.__kv_model_storage = dict()
        self.__kv_alert_storage = dict()

    def save_model(self, key: str, model: AnomalyDetectionModel):
        self.__kv_model_storage[key] = model
    
    def get_model(self, key: str) -> (AnomalyDetectionModel | None):
        return self.__kv_model_storage.get(key)
    
    def save_alert_info(self, key: str, info: AlertInfo):
        self.__kv_alert_storage[key] = info
    
    def get_alert_info(self, key: str) -> AlertInfo | None:
        return self.__kv_alert_storage.get(key)
    
    

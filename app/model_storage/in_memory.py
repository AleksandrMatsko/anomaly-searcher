

from app.model.model import AnomalyDetectionModel
from .storage import ModelStorage

class InMemoryStorage(ModelStorage):
    __kv_storage : dict

    def __init__(self):
        self.__kv_storage = dict()

    def save_model(self, key: str, model: AnomalyDetectionModel):
        self.__kv_storage[key] = model
    
    def get_model(self, key: str) -> (AnomalyDetectionModel | None):
        return self.__kv_storage.get(key)

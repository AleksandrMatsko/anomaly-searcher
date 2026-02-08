import pickle
import redis

from dataclasses import dataclass

from app.model.model import AnomalyDetectionModel, pickle_model, unpickle_model
from app.alert import AlertInfo 

from .storage import *

@dataclass
class RedisDBConfig:    
    host : str = ""
    port : int = 0
    username : str = ""
    password : str = ""

class RedisStorage(ModelStorage, AlertInfoStorage):
    __redis : redis.Redis
    __MODELS_PATH : str = "models"
    __ALERT_INFO_PATH : str = "alert_info"

    def __init__(self, cfg : RedisDBConfig):
        self.__redis = redis.Redis(
            decode_responses=False,
            host=cfg.host,
            port=cfg.port,
            username=cfg.username,
            password=cfg.password,
        )

    def __model_key(self, key : str) -> str:
        return self.__MODELS_PATH+":"+key

    def save_model(self, key: str, model: AnomalyDetectionModel):
        dumped = pickle_model(model)
        self.__redis.set(self.__model_key(key), dumped)
    
    def get_model(self, key: str) -> (AnomalyDetectionModel | None):
        rsp = self.__redis.get(self.__model_key(key))
        return unpickle_model(rsp) # type: ignore
    
    def __alert_info_key(self, key : str) -> str:
        return self.__ALERT_INFO_PATH+":"+key
    
    def save_alert_info(self, key: str, info: AlertInfo):
        dumped = pickle.dumps(info)
        self.__redis.set(self.__alert_info_key(key), dumped)
    
    def get_alert_info(self, key: str) -> AlertInfo | None:
        rsp = self.__redis.get(self.__alert_info_key(key))
        if rsp is None:
            return None
        return pickle.loads(bytes(rsp)) # type: ignore
    
def redis_storage_from_params_(params : dict) -> RedisStorage:
    host = params.get("host")
    if host is None:
        raise ValueError("no host for redis")
    
    port = params.get("port")
    if port is None:
        raise ValueError("no port for redis")
    
    username = params.get("username", "")
    password = params.get("password", "")

    return RedisStorage(cfg=RedisDBConfig(
        host=host,
        port=int(port),
        username=username,
        password=password,
    ))
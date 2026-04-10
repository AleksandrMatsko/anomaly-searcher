from .model import AnomalyDetectionModel, MODELS_DICT
from .find_holes import HolesFinderAnomalyDetectorWrapper

default_model_type = "dummy"

def get_model_by_type(model_type: str, params: dict = {}) -> AnomalyDetectionModel:
    model_getter = MODELS_DICT.get(model_type, None)
    if model_getter:
        return HolesFinderAnomalyDetectorWrapper(model_getter(params))
    
    return HolesFinderAnomalyDetectorWrapper(MODELS_DICT[default_model_type](params))

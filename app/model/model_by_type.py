

from .model_types import ModelType
from .model import AnomalyDetectionModel
from .dummy_model import DummyAnomalyDetector

default_model_getter = lambda: (DummyAnomalyDetector())

def get_model_by_type(model_type : ModelType) -> AnomalyDetectionModel:
    if model_type == ModelType.DUMMY:
        return DummyAnomalyDetector()
    
    return default_model_getter()
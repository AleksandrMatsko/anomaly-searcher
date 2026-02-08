from .model_types import ModelType
from .model import AnomalyDetectionModel
from .random_model import RandomAnomalyDetector
from .dummy_model import DummyAnomalyDetector

default_model_getter = lambda: (RandomAnomalyDetector())

def get_model_by_type(model_type : ModelType) -> AnomalyDetectionModel:
    if model_type == ModelType.RANDOM:
        return RandomAnomalyDetector()
    
    if model_type == ModelType.DUMMY:
        return DummyAnomalyDetector()
    
    return default_model_getter()

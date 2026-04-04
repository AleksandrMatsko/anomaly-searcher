import typing
import os

import app.metrics as metrics
import app.storage as storage
import app.model as model
import app.rules as rules

MODEL_STORAGE = None

def init_model_storage_for_worker(cfg : storage.BaseStorageConfig):
    global MODEL_STORAGE
    MODEL_STORAGE = storage.storage_from_cfg(cfg=cfg)

def process_single_metric_task(metric : metrics.Metric, 
                               rule: rules.Rule,
                               ) -> typing.Dict[str, typing.Any]:
    if MODEL_STORAGE is None:
        raise Exception(f"no initialzed MODEL_STORAGE in worker proccess {os.getpid()}")

    key = f"{rule.id}:{metric.custom_name(alias_by_label_values=rule.alias_by_label_values)}"
    detector = MODEL_STORAGE.get_model(key)
    if detector is None:
        detector = model.get_model_by_type(rule.model_type, rule.model_params)
    
    is_anomaly = detector.predict_one(metric)

    MODEL_STORAGE.save_model(key, detector)

    return {
        "metric": metric,
        "is_anomaly": is_anomaly,
    }
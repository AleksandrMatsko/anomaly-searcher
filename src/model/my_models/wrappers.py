from river import anomaly

from .rolling import RollingQuantileFilter

def wrap_with_filter(anomaly_detector, protect_anomaly_detector=True):
    return anomaly.QuantileFilter(
        anomaly_detector=anomaly_detector,
        q=0.99,
        protect_anomaly_detector=protect_anomaly_detector,
    )

def wrap_with_rolling_filter(anomaly_detector, protect_anomaly_detector=True, window_size=1440):
    return RollingQuantileFilter(
        anomaly_detector=anomaly_detector,
        q=0.99,
        window_size=window_size,
        protect_anomaly_detector=protect_anomaly_detector,
    )

def wrap_with_PDA(predictor):
    return anomaly.PredictiveAnomalyDetection(
        predictive_model=predictor,
        horizon=1,
        n_std=3,
        warmup_period=70,
    )

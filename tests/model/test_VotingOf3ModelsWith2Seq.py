import pytest
from testcontainers.redis import RedisContainer

import src.metrics as metrics
from src.model import VotingOf3ModelsWith2Seq, pickle_model, unpickle_model
from src.storage import RedisStorage, RedisDBConfig

def test_model_is_pickled_and_unpickled():
    metric = metrics.Metric(
        name="test_metric",
        values=[metrics.MetricValue(60, 10)],
        queried_at=61,
        labels={"foo": "bar"},
    )

    model = VotingOf3ModelsWith2Seq()
    pickled = pickle_model(model)
    unpickled_model = unpickle_model(pickled)
    assert unpickled_model is not None, f"unpickled_model must not be None after init"

    model.predict_one(metric)

    pickled = pickle_model(model)
    unpickled_model = unpickle_model(pickled)
    assert unpickled_model is not None, f"unpickled_model must not be None after first predict"

    model = unpickled_model

    for i in range(20):
        metric.values.append(metrics.MetricValue(metric.values[-1].timestamp+60, 11))
        metric.queried_at += 60

        pickled = pickle_model(model)
        unpickled_model = unpickle_model(pickled)
        assert unpickled_model is not None, f"unpickled_model must not be None"

        model = unpickled_model

def test_model_is_stored_and_fetched_from_redis_storage():
    metric = metrics.Metric(
        name="test_metric",
        values=[metrics.MetricValue(60, 10)],
        queried_at=61,
        labels={"foo": "bar"},
    )

    model = VotingOf3ModelsWith2Seq()
    MODEL_KEY = "test_VotingOf3ModelsWith2Seq"

    with RedisContainer() as redis_container:
        redis_client = redis_container.get_client()
        storage = RedisStorage(cfg=RedisDBConfig(), redis_client=redis_client)

        storage.save_model(MODEL_KEY, model)
        unpickled_model = storage.get_model(MODEL_KEY)
        assert unpickled_model is not None, f"unpickled_model must not be None after init"

        model.predict_one(metric)

        storage.save_model(MODEL_KEY, model)
        unpickled_model = storage.get_model(MODEL_KEY)
        assert unpickled_model is not None, f"unpickled_model must not be None after first predict"

        model = unpickled_model

        for i in range(20):
            metric.values.append(metrics.MetricValue(metric.values[-1].timestamp+60, 11))
            metric.queried_at += 60

            storage.save_model(MODEL_KEY, model)
            unpickled_model = storage.get_model(MODEL_KEY)
            assert unpickled_model is not None, f"unpickled_model must not be None"

            model = unpickled_model
    

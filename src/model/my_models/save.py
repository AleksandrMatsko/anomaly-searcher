import typing
import tempfile
import os

from deep_river.base import DeepEstimator, RollingDeepEstimator
from deep_river.anomaly import Autoencoder, RollingAutoencoder

def deep_river_model_to_bytes(m: typing.Union[DeepEstimator, RollingDeepEstimator]) -> bytes:
    tmp_file_name = tempfile.mktemp()
    m.save(tmp_file_name)

    m_bytes: bytes
    with open(tmp_file_name, "rb") as f:
        m_bytes = f.read()

    os.remove(tmp_file_name)

    return m_bytes

def deep_river_model_from_bytes(b: bytes, cls: typing.Union[type[Autoencoder], type[RollingAutoencoder]]) -> typing.Union[Autoencoder, RollingAutoencoder]:
    tmp_file_name = tempfile.mktemp()

    with open(tmp_file_name, "wb") as f:
        f.write(b)

    estimator = cls.load(tmp_file_name)
    os.remove(tmp_file_name)

    return estimator


    
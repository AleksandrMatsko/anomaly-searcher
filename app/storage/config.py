from dataclasses import dataclass, field

from .storage import StorageType, Storage

from .redis_storage import redis_storage_from_params_
from .exceptions import *

@dataclass
class BaseStorageConfig:
    storage_type : StorageType = StorageType.UNKNOWN
    storage_params : dict = field(default_factory=dict)

storage_constructors = {
    StorageType.REDIS: redis_storage_from_params_
}

def storage_from_cfg(cfg : BaseStorageConfig) -> Storage:
    constructor = storage_constructors.get(cfg.storage_type)
    if constructor is not None:
        return constructor(cfg.storage_params) # type: ignore
    
    raise UnknownStorageError(f"unknown storage with type '{cfg.storage_type}'")
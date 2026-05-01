from dataclasses import dataclass, field
import typing
from omegaconf import OmegaConf, DictConfig

from src.rules import Rule
from src.metrics import BaseMetricSourceConfig
from src.alert import BaseAlerterConfig
from src.storage import BaseStorageConfig

@dataclass
class AppConfig:
    max_workers : int | None = None
    storage : BaseStorageConfig = field(default_factory=BaseStorageConfig)
    metric_sources : typing.List[BaseMetricSourceConfig] = field(default_factory=list[BaseMetricSourceConfig])
    alerter : BaseAlerterConfig = field(default_factory=BaseAlerterConfig)
    rules : typing.List[Rule] = field(default_factory=list[Rule])

def from_yaml(cfg_path : str) -> AppConfig:
    schema = OmegaConf.structured(AppConfig)
    content = OmegaConf.load(cfg_path)
    cfg = OmegaConf.merge(schema, content)

    dict_cfg = OmegaConf.to_container(cfg=cfg, resolve=True, throw_on_missing=True)

    if not OmegaConf.is_dict(cfg):
        raise TypeError("bad config type, expected dict") 
    
    dict_cfg = DictConfig(dict_cfg)

    normal_dict = dict()
    for key, val in dict_cfg.items():
        normal_dict[str(key)] = val

    return AppConfig(**normal_dict)

from dataclasses import dataclass, field
import typing

from .metric_source import MetricSourceType, MetricSource 
from .exceptions import *
from .prometheus_metric_source import init_prometheus_metric_source_from_cnfg_

@dataclass
class BaseMetricSourceConfig:
    metric_source_type : MetricSourceType = MetricSourceType.UNKNOWN
    metric_source_params : dict = field(default_factory=dict)


def init_metric_sources_from_configs(configs : list[BaseMetricSourceConfig]) -> typing.Dict[MetricSourceType, MetricSource]:
    if len(configs) == 0:
        raise EmptyConfigListError
    
    sources = dict()
    
    for conf in configs:
        if conf.metric_source_type == MetricSourceType.PROMETHEUS:
            existed = sources.get(conf.metric_source_type)
            if existed is not None:
                raise MetricSourceDuplicationError(conf.metric_source_type)
            sources[conf.metric_source_type] = init_prometheus_metric_source_from_cnfg_(conf.metric_source_params)
        else:
            raise UnknownMetricSourceError(conf.metric_source_type)
        
    return sources
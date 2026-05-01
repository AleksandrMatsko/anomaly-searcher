import typing

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


from src.metrics import MetricSourceType

@dataclass
class Rule:
    metric_source_type : MetricSourceType = MetricSourceType.UNKNOWN
    model_type : str = ""
    model_params : typing.Dict[str, typing.Any] = field(default_factory=dict)
    query : str = ""
    alias_by_label_values : typing.List[str] = field(default_factory=list)
    id : str = ""
    labels : typing.Dict[str, str] = field(default_factory=dict)
    annotations : typing.Dict[str, str] = field(default_factory=dict)


class RulesProvider(ABC):
    @abstractmethod
    async def get_rules(self) -> list[Rule]:
        pass
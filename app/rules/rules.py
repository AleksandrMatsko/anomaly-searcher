import typing

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


from app.metrics import MetricSourceType
from app.model import ModelType

@dataclass
class Rule:
    metric_source_type : MetricSourceType = MetricSourceType.UNKNOWN
    model_type : ModelType = ModelType.UNKNOWN
    query : str = ""
    id : str = ""
    labels : typing.Dict[str, str] = field(default_factory=dict)
    annotations : typing.Dict[str, str] = field(default_factory=dict)


class RulesProvider(ABC):
    @abstractmethod
    async def get_rules(self) -> list[Rule]:
        pass
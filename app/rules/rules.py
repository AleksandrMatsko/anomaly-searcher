from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.metrics import MetricSourceType

@dataclass
class Rule:
    metric_source_type : MetricSourceType = MetricSourceType.UNKNOWN
    query : str = ""
    id : str = ""


class RulesProvider(ABC):
    @abstractmethod
    async def get_rules(self) -> list[Rule]:
        pass
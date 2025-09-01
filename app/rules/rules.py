from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum

class MetricSourceType(StrEnum):
    UNKNOWN = ""
    PROMETHEUS = "prometheus"


@dataclass
class Rule:
    metric_source_type : MetricSourceType = MetricSourceType.UNKNOWN
    query : str = ""
    id : str = ""


class RulesProvider:
    @abstractmethod
    async def get_rules(self) -> list[Rule]:
        pass
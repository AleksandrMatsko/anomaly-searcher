from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
import datetime

class MetricSourceType(StrEnum):
    UNKNOWN = ""
    PROMETHEUS = "PROMETHEUS"


class MetricSource(ABC):

    @abstractmethod
    async def query(self, 
              query : str,
              interval_start : datetime.datetime,
              interval_end : datetime.datetime,
              step : str,
              additional_params : dict = {}) -> dict:
        pass

    

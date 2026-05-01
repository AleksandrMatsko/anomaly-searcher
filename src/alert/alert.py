from abc import ABC, abstractmethod
from enum import StrEnum
from dataclasses import dataclass

import src.rules as rules
import src.metrics as metrics

class AlerterType(StrEnum):
    UNKNOWN = ""
    PROMETHEUS_ALERT_MANAGER = "PROMETHEUS_ALERT_MANAGER"


class Alerter(ABC):

    @abstractmethod
    def send_alert(self, 
                   rule : rules.Rule, 
                   metric : metrics.Metric,
                   startsAt : str = "",
                   endsAt : str = "",
                   **kwargs):
        pass

class AlertState(StrEnum):
    ANOMALY = "ANOMALY"
    NORMAL = "NORMAL"

@dataclass
class AlertInfo:
    started_at : str 
    state : AlertState
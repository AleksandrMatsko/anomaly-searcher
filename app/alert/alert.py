from abc import ABC, abstractmethod
from enum import StrEnum

import app.rules as rules
import app.metrics as metrics

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
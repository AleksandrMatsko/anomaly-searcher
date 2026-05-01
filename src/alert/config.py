from dataclasses import dataclass, field

from .alert import Alerter, AlerterType
from .alert_manager import alert_manager_alerter_from_params_
from .exceptions import *


@dataclass
class BaseAlerterConfig:
    alerter_type : AlerterType = AlerterType.UNKNOWN
    alerter_params : dict = field(default_factory=dict)

def alerter_from_config(cfg : BaseAlerterConfig) -> Alerter:
    if cfg.alerter_type == AlerterType.PROMETHEUS_ALERT_MANAGER:
        return alert_manager_alerter_from_params_(cfg.alerter_params)

    raise UnknownAlerterError(f"unknown alerter '{cfg.alerter_type}'")

import typing

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin
from requests import Session
from omegaconf import OmegaConf

from app.metrics.metric import Metric
from app.rules.rules import Rule

from .alert import Alerter
from .exceptions import *


# In case of a connection failure try 2 more times
MAX_REQUEST_RETRIES = 3
# wait 1 second before retrying in case of an error
RETRY_BACKOFF_FACTOR = 1
# retry only on these status
RETRY_ON_STATUS = [408, 429, 500, 502, 503, 504]

class AlertManagerAlerterException(Exception):
    pass

class AlertManagerAlerter(Alerter):
    def __init__(self, 
                 url : str,
                 retry : typing.Optional[Retry] = None
                 ):
        
        self.url = url

        if retry is None:
            retry = Retry(
                total=MAX_REQUEST_RETRIES,
                backoff_factor=RETRY_BACKOFF_FACTOR,
                status_forcelist=RETRY_ON_STATUS,
            )

        self.__headers = {
            "Content-Type": "application/json"
        }
        self.__session = Session()
        self.__session.mount(self.url, HTTPAdapter(max_retries=retry))

    def send_alert(self,
                   rule: Rule, 
                   metric: Metric, 
                   startsAt : str = "",
                   endsAt : str = "", 
                   **kwargs):
        payload : typing.Dict[str, typing.Any] = {
            "labels": rule.labels.copy(),
            "annotations": rule.annotations.copy(),
        }

        payload["labels"]["alertname"] = rule.id
        payload["labels"]["metric"] = metric.name
        payload["labels"]["custom_metric_name"] = metric.custom_name(rule.alias_by_label_values)

        if startsAt != "":
            payload["startsAt"] = startsAt

        if endsAt != "":
            payload["endsAt"] = endsAt

        body = [payload]
        omega_conf_body = OmegaConf.create(body)
        body = OmegaConf.to_container(omega_conf_body, resolve=True)

        rsp = self.__session.post(
            url=urljoin(self.url, "/api/v2/alerts"),
            headers=self.__headers,
            json=body,
        )

        if rsp.status_code != 200:
            raise AlertManagerAlerterException(
                f"HTTP Status Code {rsp.status_code} rsp content: {rsp.content}"
            )
        
def alert_manager_alerter_from_params_(params : dict) -> AlertManagerAlerter:
    url = params.get("url", None)
    if url is None:
        raise RequiredParamNotFoundError("prometheus_url")

    return AlertManagerAlerter(
        url=url,
    )
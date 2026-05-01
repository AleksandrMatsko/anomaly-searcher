import prometheus_api_client as pac
import datetime
import asyncio

from .metric_source import MetricSource, MetricSourceType
from .exceptions import *
from .metric import *

from urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError

class PrometheusMetricSource(MetricSource):

    def __init__(self,
                 prometheus_url : str,
                 disable_ssl : bool = False,
                 headers: dict = {},
                 timeout : int = 60,
                 ):
        self.__prom = pac.PrometheusConnect(
            url=prometheus_url,
            disable_ssl=disable_ssl,
            headers=headers,
        )
        self.__TIMEOUT = timeout
        try:
            if not self.__prom.check_prometheus_connection():
                raise MetricSourceUnreachableError(MetricSourceType.PROMETHEUS)
        except (ConnectionError, MaxRetryError) as e:
                raise MetricSourceUnreachableError(MetricSourceType.PROMETHEUS, e)
        
    def __get_metric_name(self, metric_dict : dict, query : str) -> typing.Tuple[str, typing.Dict[str, str]]:
        if len(metric_dict) == 0:
            return query, {"__name__": query}

        name = metric_dict.pop("__name__", query)
        labels_list = []
        labels = {
            "__name__": name,
        }

        for k in metric_dict:
            labels_list.append(f'{k}="{metric_dict[k]}"')
            labels[k] = metric_dict[k]

        return name + "{" + ",".join(labels_list) + "}", labels
        
        
    def __decode_into_metric_list(self, 
                                  rsp : list[dict], 
                                  query : str,
                                  interval_end : datetime.datetime,
                                  ) -> list[Metric]:
        metrics = []

        for d in rsp:
            name, labels = self.__get_metric_name(d["metric"], query)

            metric_values = []
            for v in d["values"]:
                metric_values.append(
                    MetricValue(v[0], float(v[1]))
                )

            metrics.append(Metric(
                name=name, 
                values=metric_values,
                queried_at=int(interval_end.timestamp()),
                labels=labels,
                alias_support=True,
                ))

        return metrics

    async def query(self, 
              query : str,
              interval_start : datetime.datetime,
              interval_end : datetime.datetime,
              step : str,
              additional_params : dict = {}) -> list[Metric]:
        tsk = asyncio.to_thread(self.__prom.custom_query_range,
            query=query,
            start_time=interval_start,
            end_time=interval_end,
            step=step,
            timeout=self.__TIMEOUT,
            params=additional_params
        )

        res = await tsk
        
        return self.__decode_into_metric_list(res, query, interval_end)

def  init_prometheus_metric_source_from_cnfg_(args : dict) -> PrometheusMetricSource:
    prometheus_url = args.get("prometheus_url")
    if prometheus_url is None:
        raise RequiredParamNotFoundError("prometheus_url")
    
    disable_ssl = args.get("disable_ssl", False)
    if not isinstance(disable_ssl, bool):
        raise WrongParamTypeError("disable_ssl", type(disable_ssl), type(True))
    
    headers = args.get("headers", {})
    if not isinstance(headers, dict):
        raise WrongParamTypeError("headers", type(headers), type(dict))
    
    timeout = args.get("timeout", 60)
    if not isinstance(timeout, int):
        raise WrongParamTypeError("timeout", type(timeout), type(60))

    return PrometheusMetricSource(
        prometheus_url=prometheus_url,
        disable_ssl=disable_ssl,
        headers=headers,
        timeout=timeout,
    )
    


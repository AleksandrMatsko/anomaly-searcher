import prometheus_api_client as pac
import datetime
import asyncio

from .metric_source import MetricSource, MetricSourceType
from .exceptions import *
from .metric import *

class PrometheusMetricSource(MetricSource):
    __prom : pac.PrometheusConnect
    __TIMEOUT : int

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
        if not self.__prom.check_prometheus_connection():
            raise MetricSourceUnreachableError(MetricSourceType.PROMETHEUS)
        
    def __get_metric_name(self, metric_dict : dict) -> typing.Tuple[str, typing.Dict[str, str]]:
        name = metric_dict.pop("__name__")
        labels_list = []
        labels = {
            "__name__": name,
        }

        for k in metric_dict:
            labels_list.append(f'{k}="{metric_dict[k]}"')
            labels[k] = metric_dict[k]

        return name + "{" + ",".join(labels_list) + "}", labels
        
        
    def __decode_into_metric_list(self, rsp : list[dict]) -> list[Metric]:
        metrics = []

        for d in rsp:
            name, labels = self.__get_metric_name(d["metric"])

            metric_values = []
            for v in d["values"]:
                metric_values.append(
                    MetricValue(v[0], float(v[1]))
                )

            metrics.append(Metric(
                name=name, 
                values=metric_values,
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
        
        return self.__decode_into_metric_list(res)

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
    


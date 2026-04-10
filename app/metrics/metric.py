import typing
import logging
import datetime

from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MetricValue:
    timestamp : int
    value : float

    def __str__(self):
        return f"{self.timestamp}: {self.value}"
    
class Metric:

    def __init__(self, 
                 name : str,
                 values : list[MetricValue],
                 queried_at : int = 0,
                 labels : typing.Dict[str, str] = {},
                 alias_support: bool = False
                 ):
        self.name = name
        self.values = values
        self.labels = labels
        self.alias_support = alias_support
        if queried_at != 0:
            self.queried_at = queried_at
        else:
            self.queried_at = int(datetime.datetime.now().timestamp())

    def __str__(self):
        return self.name + "[" + ", ".join([v.__str__() for v in self.values]) + "]"
    
    def custom_name(self, alias_by_label_values: list = []) -> str:
        if not self.alias_support:
            return self.name
        
        if len(alias_by_label_values) == 0:
            return self.name

        result_name_parts = []
        for k in alias_by_label_values:
            lv = self.labels.get(k, None)
            if lv is not None:
                result_name_parts.append(lv)
            else:
                logger.warning(f"metric '{self.name}' does not have label '{k}'")

        if len(result_name_parts) == 0:
            return self.name
            
        return "-".join(result_name_parts)
        





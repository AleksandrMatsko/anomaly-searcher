import typing

from dataclasses import dataclass

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
                 labels : typing.Dict[str, str] = {},
                 alias_support: bool = False
                 ):
        self.name = name
        self.values = values
        self.labels = labels
        self.alias_support = alias_support

    def __str__(self):
        return self.name + "[" + ", ".join([v.__str__() for v in self.values]) + "]"
    
    def custom_name(self, alias_by_label_keys: list = []) -> str:
        if not self.alias_support:
            return self.name
        
        if len(alias_by_label_keys) == 0:
            return self.name
        
        result_name_parts = []
        for k in alias_by_label_keys:
            lv = self.labels.get(k, None)
            if lv is not None:
                result_name_parts.append(lv)
            else:
                raise KeyError(f"no label '{k}' in metric {self.name}")
            
        return "_".join(result_name_parts)
        





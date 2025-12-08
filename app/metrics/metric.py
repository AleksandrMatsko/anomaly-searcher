from dataclasses import dataclass

@dataclass
class MetricValue:
    timestamp : int
    value : float

    def __str__(self):
        return f"{self.timestamp}: {self.value}"

@dataclass
class Metric:
    name : str
    values : list[MetricValue]

    def __str__(self):
        return self.name + "[" + ", ".join([v.__str__() for v in self.values]) + "]"



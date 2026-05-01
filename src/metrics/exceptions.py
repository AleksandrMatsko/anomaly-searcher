from .metric_source import MetricSourceType


class EmptyConfigListError(Exception):
    """Custom exception raised on empty configs list"""
    
    def __init__(self):
        super().__init__("list of configs in empty")


class UnknownMetricSourceError(Exception):
    
    def __init__(self, metric_source_type : MetricSourceType): 
        self.metric_source_type = metric_source_type
        super().__init__(f"unknown metric source type {self.metric_source_type}")


class RequiredParamNotFoundError(Exception):

    def __init__(self, param_name : str):
        self.param_name = param_name
        super().__init__(f"no requred param in config: {param_name}")


class WrongParamTypeError(Exception):

    def __init__(self, param_name : str, got_type, expected_type):
        self.param_name = param_name
        self.got_type = got_type
        self.expected_type = expected_type
        super().__init__(f"wrong type of parameter {param_name} - got: '{got_type}'; expected: '{expected_type}'")


class MetricSourceDuplicationError(Exception):
    
    def __init__(self, metric_source_type : MetricSourceType):
        self.metric_source_type = metric_source_type
        super().__init__(f"duplicated metric source of type {self.metric_source_type} found")


class MetricSourceUnreachableError(Exception):

    def __init__(self, metric_source_type : MetricSourceType, e: Exception | None = None):
        self.metric_source_type = metric_source_type
        self.e = e
        msg = f"metric source of type {self.metric_source_type} is unreachable."
        if e is not None:
            msg += f" Caused by: {e}"
        super().__init__(msg)
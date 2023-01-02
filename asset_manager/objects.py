from dataclasses import dataclass


@dataclass
class TimeSeriesDetails:
    returns: list
    avg_return: float
    std_dev: float

from dataclasses import dataclass
from enum import Enum


class Interval(Enum):
    MONTH = "1M"
    THREE_MONTH = "3M"
    SIX_MONTH = "6M"
    YEAR = "1Y"
    FIVE_YEAR = "5Y"


@dataclass
class TimeSeriesDetails:
    returns: list
    avg_return: float
    std_dev: float

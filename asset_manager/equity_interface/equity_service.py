from abc import ABC, abstractmethod

from asset_manager.entities_new import Equity
from asset_manager.objects import Interval, TimeSeriesDetails


class EquityService(ABC):
    @abstractmethod
    def get_equity_prices(self, ticker: str) -> tuple[float, float]:
        # method retrieves the most recent price for the equity
        pass

    @abstractmethod
    def get_equity_year_start_price(self, ticker: str) -> float:
        # method retrieves the year start price for the equity
        pass

    @abstractmethod
    def update_equity_details(self, eq: Equity, time_interval: Interval) -> TimeSeriesDetails:
        # method computes average daily return for the equity
        pass

from abc import ABC, abstractmethod

from asset_manager.entities import Equity
from asset_manager.objects import Interval, TimeSeriesDetails


class EquityService(ABC):
    @abstractmethod
    def get_equity_prices(self, ticker: str) -> tuple[float, float]:
        """Method retrieves the current price and previous day price for the equity

        Args:
            ticker (str): stock ticker

        Returns:
            tuple[float, float]: current day price, previous day price
        """
        pass

    @abstractmethod
    def get_equity_year_start_price(self, ticker: str) -> float:
        """Method retrieves the year start price for the equity

        Args:
            ticker (str): stock ticker

        Returns:
            float: year start price
        """
        pass

    @abstractmethod
    def update_equity_details(
        self, eq: Equity, time_interval: Interval
    ) -> TimeSeriesDetails:
        """Method computes returns, average return, and standard deviation for the equity over the provided interval

        Args:
            eq (Equity): object for equity in portfolio
            time_interval (Interval): time period to calculate returns and statistics

        Returns:
            TimeSeriesDetails: object containing statistics for the equity over the interval
        """
        pass

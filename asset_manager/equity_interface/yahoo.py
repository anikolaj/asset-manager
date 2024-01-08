import os
import pandas as pd
from datetime import datetime, timedelta
from yahooquery import Ticker

from asset_manager.entities_new import Equity
from asset_manager.equity_interface import EquityService
from asset_manager.equity_interface.helpers import (
    calculate_time_series_details,
    parse_prices_for_time_interval,
)
from asset_manager.objects import Interval, TimeSeriesDetails


class YahooService(EquityService):
    def __init__(self) -> None:
        pass

    def get_equity_prices(self, ticker: str) -> tuple[float, float]:
        stock = Ticker(ticker)
        price_info = stock.price[ticker]
        return (
            round(price_info["regularMarketPrice"], 2),
            round(price_info["regularMarketPreviousClose"], 2),
        )

    def get_equity_year_start_price(self, ticker: str) -> float:
        print(f"getting year start price - {ticker}")
        current_year = datetime.today().year

        stock = Ticker(ticker)
        stock_history = stock.history(
            start=f"{current_year}-01-01", end=f"{current_year}-01-07"
        )

        return stock_history.iloc[0]["open"]

    def update_equity_details(
        self, eq: Equity, time_interval: Interval
    ) -> TimeSeriesDetails:
        now_time = datetime.today()

        to_date = now_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        from_date = to_date - timedelta(days=10 * 365)

        ticker_directory = f"{os.getcwd()}/asset_manager/data/equity/{eq.ticker}"

        if os.path.exists(ticker_directory) is False:
            os.makedirs(ticker_directory)

        filename = f"{ticker_directory}/{to_date.date()}.csv"

        if os.path.exists(filename) is False:
            print("making request to yahoofinance api")
            stock = Ticker(eq.ticker)
            price_data = stock.history(
                start=from_date.date(), end=to_date.date(), interval="1mo"
            )

            # save response to file in directory
            price_data.to_csv(filename)
        else:
            price_data = pd.read_csv(filename)

        monthly_prices = list(price_data["close"])
        time_series = parse_prices_for_time_interval(monthly_prices, time_interval)

        return calculate_time_series_details(time_series)

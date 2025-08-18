import os
import pandas as pd
import yfinance as yf
from datetime import date, datetime, timedelta

from asset_manager.database.entities import Equity
from asset_manager.equity_service import EquityService
from asset_manager.equity_service.helpers import (
    calculate_time_series_details,
    parse_prices_for_time_interval,
)
from asset_manager.objects import Interval, TimeSeriesDetails


class YahooService(EquityService):
    def __init__(self) -> None:
        pass

    def get_equity_prices(self, ticker: str) -> tuple[float, float]:
        stock = yf.Ticker(ticker)
        stock_info = stock.info

        return (
            round(stock_info["currentPrice"], 2),
            round(stock_info["previousClose"], 2),
        )

    def get_price_history(
        self, ticker: str, start_date: date, end_date: date
    ) -> dict[date, float]:
        start = start_date.isoformat()
        end = (end_date + timedelta(days=1)).isoformat()

        history = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

        # determine closing prices
        if "Adj Close" in history.columns:
            prices: pd.Series = history["Adj Close"][ticker]
        else:
            prices: pd.Series = history["Close"][ticker]

        prices_dict: dict[pd.DatetimeIndex, float] = prices.to_dict()

        return {dti.date(): price for dti, price in prices_dict.items()}

    def get_equity_year_start_price(self, ticker: str) -> float:
        print(f"getting year start price - {ticker}")
        current_year = datetime.today().year

        stock = yf.Ticker(ticker)
        stock_history = stock.history(
            start=f"{current_year}-01-01", end=f"{current_year}-01-07"
        )

        return stock_history.iloc[0]["Open"]

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

            stock = yf.Ticker(eq.ticker)
            price_data = stock.history(
                start=from_date.date(), end=to_date.date(), interval="1mo"
            )

            # save response to file in directory
            price_data.to_csv(filename)
        else:
            price_data = pd.read_csv(filename)

        monthly_prices = list(price_data["Close"])
        time_series = parse_prices_for_time_interval(monthly_prices, time_interval)

        return calculate_time_series_details(time_series)

import datetime
import json
import os
import requests

from asset_manager.entities_new import Equity
from asset_manager.equity_service import EquityService
from asset_manager.equity_service.helpers import (
    calculate_time_series_details,
    parse_prices_for_time_interval,
)
from asset_manager.objects import Interval, TimeSeriesDetails


class FinnhubService(EquityService):
    # finnhub API constants
    __STOCK_QUOTE = "https://finnhub.io/api/v1/quote?symbol={}&token={}"
    __STOCK_DATA = "https://finnhub.io/api/v1/stock/candle?symbol={}&resolution={}&from={}&to={}&token={}"

    def __init__(self, config: dict) -> None:
        self.__key = config["finnhub"]["key"]

    def get_equity_prices(self, ticker: str) -> tuple[float, float]:
        api_string = self.__STOCK_QUOTE.format(ticker, self.__key)
        quote = requests.get(api_string).json()
        return (round(quote["c"], 2), round(quote["pc"], 2))

    def get_equity_year_start_price(self, ticker: str) -> float:
        print(f"getting year start price - {ticker}")
        current_year = datetime.datetime.today().year

        # check if year start already exists for the given ticker
        year_start_file = f"./asset_manager/data/equity/{ticker}/year_start.json"

        if os.path.exists(year_start_file):
            with open(year_start_file, "r") as data_file:
                year_start_data = json.load(data_file)

            if year_start_data["year"] == current_year:
                return year_start_data["yearStartPrice"]
        else:
            year_start_data = {}

        first_trading_day = self.__get_first_trading_day_of_year()
        unix_time = int(first_trading_day.timestamp())

        api_string = self.__STOCK_DATA.format(
            ticker, "D", unix_time, unix_time, self.__key
        )
        response = requests.get(api_string).json()

        # need to handle case when first trading day of the year does not have quote for given equity
        if len(response["c"]) == 0:
            year_start_price = float(
                input("ERROR retrieving year strice price, please manually enter = ")
            )
        else:
            year_start_price = response["c"][0]

        # save year start price for ticker to the data folder
        year_start_data["yearStartPrice"] = year_start_price
        year_start_data["year"] = current_year

        with open(year_start_file, "w") as data_file:
            json.dump(year_start_data, data_file)

        return year_start_price

    def update_equity_details(
        self, eq: Equity, time_interval: Interval
    ) -> TimeSeriesDetails:
        now_time = datetime.datetime.today()

        to_date = now_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        from_date = to_date - datetime.timedelta(days=10 * 365)

        ticker_directory = f"{os.getcwd()}/asset_manager/data/equity/{eq.ticker}"

        if os.path.exists(ticker_directory) is False:
            os.makedirs(ticker_directory)

        filename = f"{ticker_directory}/{to_date.date()}.json"
        response = {}

        if os.path.exists(filename) is False:
            print("making request to finnhub.io api")
            from_unix = int(from_date.timestamp())
            to_unix = int(to_date.replace(day=2).timestamp())
            api_string = self.__STOCK_DATA.format(
                eq.ticker, "M", from_unix, to_unix, self.__key
            )
            response = requests.get(api_string).json()

            # save response to file in directory
            with open(filename, "w") as json_file:
                json.dump(response, json_file)
        else:
            with open(filename, "r") as json_file:
                response = json.load(json_file)

        monthly_prices = response["c"]
        time_series = parse_prices_for_time_interval(monthly_prices, time_interval)

        return calculate_time_series_details(time_series)

    def __get_first_trading_day_of_year(self) -> datetime.datetime:
        with open("asset_manager/global_data.json", "r") as data_file:
            global_data = json.load(data_file)

        first_trading_day = datetime.datetime.fromisoformat(
            global_data["firstTradingDay"]
        )
        today_date = datetime.datetime.today().date()

        if first_trading_day.year != today_date.year:
            first_day = input(
                "Please enter the first trading of the current year (YYYY-MM-DD) = "
            )
            first_trading_day = datetime.datetime.fromisoformat(first_day)
            global_data["firstTradingDay"] = first_day

            with open("asset_manager/global_data.json", "w") as data_file:
                json.dump(global_data, data_file)

        return first_trading_day

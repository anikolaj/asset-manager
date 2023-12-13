import datetime
import requests
import statistics
import os
import pandas as pd
import json
from scipy.stats import gmean
from yahooquery import Ticker

from asset_manager.entities_new import Equity
from asset_manager.objects import Interval, TimeSeriesDetails
from asset_manager.constants import STOCK_DATA, STOCK_QUOTE

FINNHUB_KEY = ""


# method sets api key used for finnhub.io api
def set_api_key(config: dict) -> None:
    global FINNHUB_KEY
    FINNHUB_KEY = config["finnhub"]["key"]


# method retrieves the most recent price for the equity using finnhub api
def get_equity_prices_finnhub(ticker: str) -> tuple[float, float]:
    api_string = STOCK_QUOTE.format(ticker, FINNHUB_KEY)
    quote = requests.get(api_string).json()
    return (round(quote["c"], 2), round(quote["pc"], 2))


# method retrieves the most recent price for the equity using yahoo finance
def get_equity_prices_yahoo(ticker: str) -> tuple[float, float]:
    stock = Ticker(ticker)
    price_info = stock.price[ticker]
    return (round(price_info["regularMarketPrice"], 2), round(price_info["regularMarketPreviousClose"], 2))


# method retrieves the year start price for the equity
def get_equity_year_start_price(ticker: str) -> float:
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

    first_trading_day = get_first_trading_day_of_year()
    unix_time = int(first_trading_day.timestamp())

    api_string = STOCK_DATA.format(ticker, "D", unix_time, unix_time, FINNHUB_KEY)
    response = requests.get(api_string).json()

    # need to handle case when first trading day of the year does not have quote for given equity
    if len(response["c"]) == 0:
        year_start_price = float(input("ERROR retrieving year strice price, please manually enter = "))
    else:
        year_start_price = response["c"][0]

    # save year start price for ticker to the data folder
    year_start_data["yearStartPrice"] = year_start_price
    year_start_data["year"] = current_year

    with open(year_start_file, "w") as data_file:
        json.dump(year_start_data, data_file)

    return year_start_price


# method computes average daily return for the equity using finnhub api
def update_equity_details_finnhub(eq: Equity, time_interval: Interval) -> TimeSeriesDetails:
    now_time = datetime.datetime.today()

    to_date = now_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    from_date = to_date - datetime.timedelta(days=10*365)

    ticker_directory = f"{os.getcwd()}/asset_manager/data/equity/{eq.ticker}"

    if os.path.exists(ticker_directory) is False:
        os.makedirs(ticker_directory)

    filename = f"{ticker_directory}/{to_date.date()}.json"
    response = {}

    if os.path.exists(filename) is False:
        print("making request to finnhub.io api")
        from_unix = int(from_date.timestamp())
        to_unix = int(to_date.replace(day=2).timestamp())
        api_string = STOCK_DATA.format(eq.ticker, "M", from_unix, to_unix, FINNHUB_KEY)
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


# method computes average daily return for the equity using yahoo finance
def update_equity_details_yahoo(eq: Equity, time_interval: Interval) -> TimeSeriesDetails:
    now_time = datetime.datetime.today()

    to_date = now_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    from_date = to_date - datetime.timedelta(days=10*365)

    ticker_directory = f"{os.getcwd()}/asset_manager/data/equity/{eq.ticker}"

    if os.path.exists(ticker_directory) is False:
        os.makedirs(ticker_directory)

    filename = f"{ticker_directory}/{to_date.date()}.csv"

    if os.path.exists(filename) is False:
        print("making request to yahoofinance api")
        stock = Ticker(eq.ticker)
        price_data = stock.history(start=from_date.date(), end=to_date.date(), interval="1mo")

        # save response to file in directory
        price_data.to_csv(filename)
    else:
        price_data = pd.read_csv(filename)

    monthly_prices = list(price_data["close"])
    time_series = parse_prices_for_time_interval(monthly_prices, time_interval)

    return calculate_time_series_details(time_series)


# method will parse out the relevant time series array from the monthly stock prices
def parse_prices_for_time_interval(monthly_prices: list, time_interval: Interval) -> list:
    if time_interval == Interval.MONTH:
        return monthly_prices

    split_value = 0

    if time_interval == Interval.THREE_MONTH:
        split_value = 3
    elif time_interval == Interval.SIX_MONTH:
        split_value = 6
    elif time_interval == Interval.YEAR:
        split_value = 12
    elif time_interval == Interval.FIVE_YEAR:
        split_value = 60
    else:
        print("invalid time interval provided!")
        return []

    return monthly_prices[::split_value]


# method will calculate the returns array, average return, and risk
def calculate_time_series_details(time_series: list) -> TimeSeriesDetails:
    total_samples = len(time_series)

    percent_changes = []
    returns = []

    for i in range(total_samples-1, 0, -1):
        present_price = time_series[i]
        previous_price = time_series[i-1]

        percent_change = present_price / previous_price
        rate_of_return = percent_change - 1

        percent_changes.append(percent_change)
        returns.append(rate_of_return)

    stdev = None
    if len(returns) > 1:
        stdev = statistics.stdev(returns)

    return TimeSeriesDetails(returns, gmean(percent_changes)-1, stdev)


def get_first_trading_day_of_year() -> datetime.datetime:
    with open("asset_manager/global_data.json", "r") as data_file:
        global_data = json.load(data_file)

    first_trading_day = datetime.datetime.fromisoformat(global_data["firstTradingDay"])
    today_date = datetime.datetime.today().date()

    if first_trading_day.year != today_date.year:
        first_day = input("Please enter the first trading of the current year (YYYY-MM-DD) = ")
        first_trading_day = datetime.datetime.fromisoformat(first_day)
        global_data["firstTradingDay"] = first_day

        with open("asset_manager/global_data.json", "w") as data_file:
            json.dump(global_data, data_file)

    return first_trading_day

import requests
import statistics
import os
import json
from datetime import datetime, timedelta
from scipy.stats import gmean

from asset_manager.entities_new import Equity
from asset_manager.objects import TimeSeriesDetails
from asset_manager.constants import STOCK_DATA, STOCK_QUOTE

FINNHUB_KEY = ""


# method sets api key used for finnhub.io api
def set_api_key(config: dict) -> None:
    global FINNHUB_KEY
    FINNHUB_KEY = config["finnhub"]["key"]


# method retrieves the most recent price for the equity
def get_equity_price(eq: Equity) -> float:
    api_string = STOCK_QUOTE.format(eq.ticker, FINNHUB_KEY)
    quote = requests.get(api_string).json()
    return round(quote["c"], 2)


# method retrieves the year start price for the equity
def get_equity_year_start_price(eq: Equity) -> float:
    print(f"getting year start price - {eq.ticker}")

    # check if year start already exists for the given ticker
    year_start_file = os.getcwd() + "/asset_manager/data/equity/{}/year_start.json"
    year_start_file = year_start_file.format(eq.ticker)

    current_year = datetime.today().year
    year_start_data = {}

    if os.path.exists(year_start_file):
        with open(year_start_file, "r") as data_file:
            year_start_data = json.load(data_file)

        if year_start_data["year"] == current_year:
            return year_start_data["yearStartPrice"]

    first_trading_day = get_first_trading_day_of_year()
    unix_time = first_trading_day.strftime("%s")

    api_string = STOCK_DATA.format(eq.ticker, "D", unix_time, unix_time, FINNHUB_KEY)
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


# method computes average daily return for the equity
def update_equity_details(eq: Equity, time_interval: str) -> TimeSeriesDetails:
    now_time = datetime.today()
    from_date = ""
    to_date = ""

    to_date = now_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    from_date = to_date - timedelta(days=10*365)
    resolution = "M"

    current_directory = os.getcwd()
    daily_directory = current_directory + "/asset_manager/data/equity/{}/"
    daily_directory = daily_directory.format(eq.ticker)

    if os.path.exists(daily_directory) is False:
        os.makedirs(daily_directory)
    os.chdir(daily_directory)

    filename = f"{to_date.date()}.json"
    response = {}

    if os.path.exists(filename) is False:
        print("making request to finnhub.io api")
        from_unix = int(from_date.timestamp())
        to_unix = int(to_date.replace(day=2).timestamp())
        api_string = STOCK_DATA.format(eq.ticker, resolution, from_unix, to_unix, FINNHUB_KEY)
        response = requests.get(api_string).json()

        # save response to file in directory
        with open(filename, "w") as json_file:
            json.dump(response, json_file)
    else:
        with open(filename, "r") as json_file:
            response = json.load(json_file)

    os.chdir(current_directory)

    monthly_prices = response["c"]
    time_series = parse_prices_for_time_interval(monthly_prices, time_interval)

    return calculate_time_series_details(time_series)


# method will parse out the relevant time series array from the monthly stock prices
def parse_prices_for_time_interval(monthly_prices: list, time_interval: str) -> list:
    if time_interval == "1M":
        return monthly_prices

    split_value = 0

    if time_interval == "1Q":
        split_value = 3
    elif time_interval == "2Q":
        split_value = 6
    elif time_interval == "1Y":
        split_value = 12
    elif time_interval == "5Y":
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


def get_first_trading_day_of_year() -> datetime.date:
    global_data = {}
    with open("asset_manager/global_data.json", "r") as data_file:
        global_data = json.load(data_file)

    first_trading_day = datetime.fromisoformat(global_data["firstTradingDay"]).date()
    today_date = datetime.today().date()

    # below condition is for new year when we need to recalculate the first trading day
    if first_trading_day.year != today_date.year:
        d = datetime(today_date.year, 1, 2).date()

        while d.weekday() == 5 or d.weekday() == 6:
            d += timedelta(days=1)

        first_trading_day = d
        global_data["firstTradingDay"] = first_trading_day.isoformat()

        with open("asset_manager/global_data.json", "w") as data_file:
            json.dump(global_data, data_file)

    return first_trading_day

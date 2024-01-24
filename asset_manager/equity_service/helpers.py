from statistics import stdev
from scipy.stats import gmean

from asset_manager.objects import Interval, TimeSeriesDetails


def parse_prices_for_time_interval(
    monthly_prices: list, time_interval: Interval
) -> list:
    """Method will parse out the relevant time series array from the monthly stock prices

    Args:
        monthly_prices (list): list of monthly prices for the stock
        time_interval (Interval): time period to split prices

    Returns:
        list: list of prices representing the time interval
    """

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


def calculate_time_series_details(time_series: list) -> TimeSeriesDetails:
    """Method will calculate the returns array, average return, and risk

    Args:
        time_series (list): list of prices for the time interval

    Returns:
        TimeSeriesDetails: object containing statistics for the time series
    """

    total_samples = len(time_series)

    percent_changes = []
    returns = []

    for i in range(total_samples - 1, 0, -1):
        present_price = time_series[i]
        previous_price = time_series[i - 1]

        percent_change = present_price / previous_price
        rate_of_return = percent_change - 1

        percent_changes.append(percent_change)
        returns.append(rate_of_return)

    return TimeSeriesDetails(returns, gmean(percent_changes) - 1, stdev(returns))

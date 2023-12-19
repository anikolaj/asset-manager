import statistics
from scipy.stats import gmean

from asset_manager.objects import Interval, TimeSeriesDetails


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

import requests
import statistics
import os
import json
import time
from datetime import date, timedelta

from asset_manager.entities import *
from asset_manager.objects import *
from asset_manager.constants import *

FINNHUB_KEY = ""

# method sets api key used for finnhub.io api
def set_api_key(config):
	global FINNHUB_KEY
	FINNHUB_KEY = config["finnhub"]["key"]

# method retrieves the most recent price for the equity
def get_equity_price(eq):
	api_string = STOCK_QUOTE.format(eq.ticker, FINNHUB_KEY)
	quote = requests.get(api_string).json()
	return quote["c"]

# method computes average daily return for the equity
def update_equity_details(eq, time_interval):
	today = date.today()
	from_date = ""
	to_date = ""
	timeseries_key = ""
	
	if time_interval == "Daily":
		to_date = today
		from_date = to_date - timedelta(days=1*365)
		resolution = "D"
	elif time_interval == "Weekly":
		to_date = today - timedelta(days=today.weekday())
		from_date = to_date - timedelta(days=5*365)
		resolution = "W"
	elif time_interval == "Monthly":
		to_date = today.replace(day=1)
		from_date = to_date - timedelta(days=5*365)
		resolution = "M"
	elif time_interval == "Yearly":
		print("yearly setup needs tweaking!")
		return
		working_date = today.replace(month=1).replace(day=1)
	else:
		print("invalid time interval provided")
		return
	
	current_directory = os.getcwd()
	daily_directory = current_directory + "/asset_manager/data/equity/{}/{}/"
	daily_directory = daily_directory.format(eq.ticker, time_interval)
	
	if os.path.exists(daily_directory) == False:
		os.makedirs(daily_directory)
	os.chdir(daily_directory)
	
	filename = str(to_date) + ".json"
	response = {}
		
	if os.path.exists(filename) == False:
		print("making request to finnhub.io api")
		from_unix = from_date.strftime("%s")
		to_unix = to_date.strftime("%s")
		api_string = STOCK_DATA.format(eq.ticker, resolution, from_unix, to_unix, FINNHUB_KEY)
		response = requests.get(api_string).json()
		
		# save response to file in directory
		with open(filename, "w") as json_file:
			json.dump(response, json_file)
	else:
		with open(filename, "r") as json_file:
			response = json.load(json_file)
		
	os.chdir(current_directory)
		
	time_series = response["c"]
	total_samples = len(time_series)
	current_price = time_series[total_samples - 1]
	percent_changes = []
		
	for i in range(total_samples-1, 1, -1):
		present_price = time_series[i]
		previous_price = time_series[i-1]
			
		percent_change = (present_price / previous_price) - 1
		percent_changes.append(percent_change)

	return TimeSeriesDetails(percent_changes, statistics.mean(percent_changes), statistics.stdev(percent_changes))
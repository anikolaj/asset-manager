import os
import json
import requests
from datetime import date

from asset_manager.constants import *
import asset_manager.rates as rates

IEX_KEY = ""

# TREASURY SYMBOLS
DGS30 = "DGS30"
DGS10 = "DGS10"
DGS5 = "DGS5"
DGS1 = "DGS1"
DGS6MO = "DGS6MO"
DGS3MO = "DGS3MO"
DGS1MO = "DGS1MO"

# method sets api key used for IEX Cloud api
def set_api_key(config):
	global IEX_KEY
	IEX_KEY = config["iex"]["key"]

# method sets all the treasury rates for the app
def get_all_treasury_rates():
	rates.UST30Y = get_treasury_rate(DGS30)
	rates.UST10Y = get_treasury_rate(DGS10)
	rates.UST5Y = get_treasury_rate(DGS5)
	rates.UST1Y = get_treasury_rate(DGS1)
	rates.UST6MO = get_treasury_rate(DGS6MO)
	rates.UST3MO = get_treasury_rate(DGS3MO)
	rates.UST1MO = get_treasury_rate(DGS1MO)

# method retrieves the treasury rate for the given symbol
def get_treasury_rate(symbol):
	today = date.today()

	current_directory = os.getcwd()
	symbol_directory = current_directory + "/asset_manager/data/treasury/{}/"
	symbol_directory = symbol_directory.format(symbol)

	if os.path.exists(symbol_directory) == False:
		os.makedirs(symbol_directory)
	os.chdir(symbol_directory)
	
	filename = str(today) + ".json"
	response = {}
		
	if os.path.exists(filename) == False:
		api_string = TREASURY_RATE.format(symbol, IEX_KEY)
		response = requests.get(api_string).json()
		
		# save response to file in directory
		with open(filename, "w") as json_file:
			json.dump(response, json_file)
	else:
		with open(filename, "r") as json_file:
			response = json.load(json_file)
		
	os.chdir(current_directory)

	rate = response[0]["value"]
	return rate
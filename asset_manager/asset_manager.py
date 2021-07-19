import sys
import json
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import asset_manager.database as db
import asset_manager.equity_service as equity_service
import asset_manager.treasury_service as treasury_service
import asset_manager.cli as cli
import asset_manager.rates as rates
from asset_manager.portfolio_analyzer import PortfolioAnalyzer
from asset_manager.cli import cli
from asset_manager.entities import *

# application launch point
def main():
	print("launching asset manager")
	configure_services()
	
	# get portfolio specified on command line
	p = retrieve_portfolio()
	if p is None: return
	
	# retrieve treasury rates
	treasury_service.get_all_treasury_rates()
	
	# construct portfolio analyzer and update details
	portfolio_analyzer = PortfolioAnalyzer(p)
	portfolio_analyzer.analyze()
	
	# output equities
	log_equities(p)
	
	# output treasury rates
	log_treasuries()
	
	# add call to method to prompt CLI for executing portfolio commands
	portfolio_prompt = cli(portfolio_analyzer)
	portfolio_prompt.run_prompt()

# import credentials to connect to external services
def configure_services():
	config = {}
	with open("asset_manager/config.yml", "r") as config_file:
		config = yaml.safe_load(config_file)
	
	db.open_connection(config)
	equity_service.set_api_key(config)
	treasury_service.set_api_key(config)

# get portfolio or create a new one
def retrieve_portfolio():
	portfolio_name = sys.argv[1]
	p = db.get_portfolio_by_name(portfolio_name)
	
	# validate if portfolio exists and create new one if desired
	if p is None:
		create_new = input(portfolio_name + " does not exist. Would you like to create one with this name (y/n) = ")
		if create_new == "y":
			p = db.create_portfolio(portfolio_name)
		else:
			print("....exiting application")
			return
	
	print("portfolio id = " + str(p.id))

	return p

# method handles logging equities in the specified portfolio
def log_equities(p):
	print("CURRENT EQUITIES IN PORTFOLIO")
	for eq in p.equities:
		print(eq.ticker + " - " + str(eq.price))

	print("")

# method handles logging treasury rates
def log_treasuries():
	print("CURRENT TREASURY RATES")
	print("US 5 Year = " + str(rates.UST5Y))
	print("US 1 Year = " + str(rates.UST1Y))
	print("US 6 Month = " + str(rates.UST6MO))
	print("US 3 Month = " + str(rates.UST3MO))
	print("US 1 Month = " + str(rates.UST1MO))
	print("")
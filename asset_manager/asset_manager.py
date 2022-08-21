import sys
import yaml

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
	print("")
	configure_services()
	
	# get portfolio specified on command line
	p = retrieve_portfolio()
	if p is None: return
	
	# retrieve treasury rates
	treasury_service.get_all_treasury_rates()
	
	# construct portfolio analyzer and update details
	portfolio_analyzer = PortfolioAnalyzer(p)
	portfolio_analyzer.analyze()

	# output cash
	log_cash(p)
	
	# output equities
	log_equities(p)
	
	# output treasury rates
	# log_treasuries()
	
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
		create_new = input(f"{portfolio_name} does not exist. Would you like to create one with this name (y/n) = ")
		if create_new == "y":
			p = db.create_portfolio(portfolio_name)
		else:
			print("....exiting application")
			return
	
	print(f"PORTFOLIO ID - {p.id}")

	return p

# method handles logging cash balance in the specified portfolio
def log_cash(p):
	print("- CASH")
	print(f"{p.cash} USD")
	print("")

# method handles logging equities in the specified portfolio
def log_equities(p):
	print("- EQUITIES")
	print("ticker" + "\t" + "price" + "\t" + "shares" + "\t" + "ytd")
	for eq in p.equities:
		print(eq.ticker + "\t" + str(eq.price) + "\t" + str(eq.shares) + "\t" + f"{str(round(eq.ytd * 100, 2))}%")

	print("")

# method handles logging treasuries in the specified portfolio
# def log_treasuries():
# 	print("LOG PORTFOLIO TREASURIES HERE")
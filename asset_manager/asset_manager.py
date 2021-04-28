import sys
import json
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import asset_manager.database as db
import asset_manager.equity_service as equity_service
import asset_manager.cli as cli
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
	
	# update assets in portfolio with current
	portfolio_analyzer = PortfolioAnalyzer(p)
	
	print("CURRENT EQUITIES IN PORTFOLIO")
	for eq in p.equities:
		print(eq.ticker + " - " + str(eq.price))
	
	# analyze the portfolio of assets
	portfolio_analyzer.analyze()

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

# run analysis on portfolio details
def analyze(portfolio_analyzer):
	# retrieve asset information
	portfolio_analyzer.update_equities()
	
	# compute portfolio total value
	portfolio_analyzer.compute_total_value()

	for time_interval in ["1M", "1Q", "2Q", "1Y", "5Y"]:
		# compute features w, m, and C
		portfolio_analyzer.compute_features(time_interval)
		
		# compute expected return, variance, and minimum variance portfolios
		portfolio_analyzer.compute_expected_return(time_interval)
		portfolio_analyzer.compute_variance(time_interval)
		portfolio_analyzer.compute_minimum_variance_portfolio(time_interval)

		# compute the minimum variance line
		portfolio_analyzer.compute_minimum_variance_line(time_interval)
	
	print("---- PORTFOLIO EXPECTED RETURN ----")
	expected_returns = json.dumps(portfolio_analyzer.expected_return, indent=2)
	print(expected_returns)
	
	print("---- PORTFOLIO STANDARD DEVIATION ----")
	standard_deviations = json.dumps(portfolio_analyzer.standard_deviation, indent=2)
	print(standard_deviations)
	
	print("---- MINIMUM VARIANCE PORTFOLIOS ----")
	mvps = json.dumps(portfolio_analyzer.mvp, indent=2)
	print(mvps)
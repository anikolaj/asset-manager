import sys
import json
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import asset_manager.database as db
import asset_manager.equity_service as equity_service
from asset_manager.portfolio_analyzer import PortfolioAnalyzer
from asset_manager.excel_utility import ExcelUtility
from asset_manager.entities import *

# application launch point
def launch():
	print("launching asset manager")
	configure_services()
	
	portfolio_name = sys.argv[1]
	p = db.get_portfolio_by_name(portfolio_name)
	print("portfolio id = " + str(p.id))
	
	# validate if portfolio exists and create new one if desired
	if p is None:
		create_new = input(portfolio_name + " does not exist. Would you like to create one with this name (y/n) = ")
		if create_new == "y":
			# portfolio_id = database.create_portfolio(create_new)
			pass
		else:
			return
	
	# update assets in portfolio with current
	portfolio_analyzer = PortfolioAnalyzer(p)
	portfolio_analyzer.update_equities()
	
	print("EQUITIES IN PORTFOLIO")
	for eq in p.equities:
		print(eq.ticker + " - " + str(eq.price))
	
	# compute portfolio total value
	portfolio_analyzer.compute_total_value()
	
	# compute feature vectors describing portfolio
	portfolio_analyzer.compute_features("Daily")
	portfolio_analyzer.compute_features("Weekly")
	portfolio_analyzer.compute_features("Monthly")
	
	# compute expected portfolio return
	portfolio_analyzer.compute_expected_return("Daily")
	portfolio_analyzer.compute_expected_return("Weekly")
	portfolio_analyzer.compute_expected_return("Monthly")
	print("---- PORTFOLIO EXPECTED RETURN ----")
	expected_returns = json.dumps(portfolio_analyzer.expected_return, indent=2)
	print(expected_returns)
	
	# compute variance and standard deviation
	portfolio_analyzer.compute_variance("Daily")
	portfolio_analyzer.compute_variance("Weekly")
	portfolio_analyzer.compute_variance("Monthly")
	print("---- PORTFOLIO STANDARD DEVIATION ----")
	standard_deviations = json.dumps(portfolio_analyzer.standard_deviation, indent=2)
	print(standard_deviations)
	
	# compute the minimum variance portfolio
	portfolio_analyzer.compute_minimum_variance_portfolio("Daily")
	portfolio_analyzer.compute_minimum_variance_portfolio("Weekly")
	portfolio_analyzer.compute_minimum_variance_portfolio("Monthly")
	print("---- MINIMUM VARIANCE PORTFOLIOS ----")
	mvps = json.dumps(portfolio_analyzer.mvp, indent=2)
	print(mvps)
	
	# reweight portfolio to mvp
	reweight = input("would you like to reweight based on minimum variance portfolio (y/n) = ")
	if reweight == "y":
		time_interval = input("what time interval for reweight (Daily, Weekly, Monthly) = ")
		portfolio_analyzer.reweight_to_mvp(time_interval)
		portfolio_analyzer.compute_expected_return(time_interval)
		portfolio_analyzer.compute_variance(time_interval)
	
	# purchase new assets
	purchase_equity = input("would you like to order new equity (y/n) = ")
	while purchase_equity == "y":
		ticker = input("enter ticker = ")
		shares = input("number of shares = ")
		portfolio_analyzer.add_equity_to_portfolio(ticker, shares)

		purchase_equity = input("would you like to order another equity (y/n) = ")

	# write results to excel workbook
	generate_excel = input("write results to excel workbook (y/n) = ")
	if generate_excel == "y":
		excel_utility = ExcelUtility(portfolio_analyzer)
		excel_utility.generate_portfolio_workbook()

# import credentials to connect to external services
def configure_services():
	config = {}
	with open("asset_manager/config.yml", "r") as config_file:
		config = yaml.safe_load(config_file)
	
	db.open_connection(config)
	equity_service.set_api_key(config)
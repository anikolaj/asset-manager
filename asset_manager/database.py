from mongoengine import connect

from asset_manager.entities import *

# this class will handle all the queries to the asset manager database

# open engine for mongodb database
def open_connection(config):
	connect(
		db=config["mongodb"]["db"],
		username=config["mongodb"]["username"],
		password=config["mongodb"]["password"],
		host=config["mongodb"]["host"]
	)

# method handles checking if portfolio exists in database
def get_portfolio_by_name(portfolio_name):
	portfolio_entity = None
	
	portfolio_entities = Portfolio.objects(name=portfolio_name)
	if len(portfolio_entities) > 0:
		portfolio_entity = portfolio_entities.get()
	
	return portfolio_entity

# method handles adding a portfolio to the asset manager database
def create_portfolio(portfolio_name):
	portfolio = Portfolio(name=portfolio_name, value=0.0)
	portfolio.save()
	print("portfolio successfully created")

	return portfolio

# method handles adding an equity to a portfolio in the database
def add_equity_to_portfolio(portfolio, new_equity):
	portfolio.equities.append(new_equity)
	portfolio.save()

# method handles getting equity details in the database
def get_equity_by_ticker(equity_ticker):
	equity_entity = None

	equity_entities = Equity.objects(ticker=equity_ticker)
	if len(equity_entities) > 0:
		equity_entity = equity_entities.get()
	else:
		equity_entity = Equity(ticker=equity_ticker)
		equity_entity.save()

	return equity_entity
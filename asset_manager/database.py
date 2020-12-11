from mongoengine import *

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
	print("checking for portfolio - " + portfolio_name)
	
	portfolio_entities = Portfolio.objects(name=portfolio_name)
	if len(portfolio_entities) > 0:
		portfolio_entity = portfolio_entities.get()
	
	return portfolio_entity

# method handles adding a portfolio to the asset manager database
def create_portfolio(portfolio_name):
	print("creating new portfolio")

# method handles adding an equity to a portfolio in the database
def add_equity_to_portfolio(portfolio, new_equity):
	portfolio.equities.append(new_equity)
	portfolio.save()
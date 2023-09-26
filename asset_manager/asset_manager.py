import sys
import yaml
from datetime import datetime

import asset_manager.equity_service as equity_service
import asset_manager.treasury_service as treasury_service
from asset_manager.database_new import Database
from asset_manager.cli import cli
from asset_manager.portfolio_analyzer import PortfolioAnalyzer
from asset_manager.entities_new import Portfolio


def main() -> None:
    # load config and configure services
    config = load_config()
    equity_service.set_api_key(config)
    treasury_service.set_api_key(config)

    # establish database connection
    db = Database(
        user=config["mongodb"]["username"],
        password=config["mongodb"]["password"],
        database=config["mongodb"]["database"],
        cluster=config["mongodb"]["cluster"]
    )

    # get portfolio specified on command line
    p = retrieve_portfolio(db)
    if p is None:
        return

    print("")
    print(f"SUMMARY DATE - {datetime.today().date()}")
    print("---------------------------------")

    # construct portfolio analyzer and update details
    portfolio_analyzer = PortfolioAnalyzer(p)
    portfolio_analyzer.analyze()
    db.save_portfolio(portfolio_analyzer.portfolio)

    # retrieve treasury rates
    treasury_service.get_all_treasury_rates()

    # output cash
    log_cash(p)

    # output equities
    log_equities(p)

    # output treasury rates
    # log_treasuries()

    # add call to method to prompt CLI for executing portfolio commands
    portfolio_prompt = cli(portfolio_analyzer=portfolio_analyzer, db=db)
    portfolio_prompt.run_prompt()


# import credentials to connect to external services
def load_config() -> dict:
    with open("asset_manager/config.yml", "r") as config_file:
        return yaml.safe_load(config_file)


def retrieve_portfolio(db: Database) -> Portfolio:
    """Retrieves portfolio specified from the command line

    Args:
        db (Database): database instance to query portfolios

    Returns:
        Portfolio: object representing the portfolio and its holdings
    """

    if len(sys.argv) > 1:
        portfolio_name = sys.argv[1]
    else:
        # retrieve all portfolios names
        portfolio_names = db.get_portfolio_names()

        # display portfolios and wait for user to select
        print("")
        print("No portfolio name provided. Please enter a portfolio name from below list.")
        for name in portfolio_names:
            print(f"\t- {name}")

        # assign selected portfolio to portfolio
        portfolio_name = input("-> ")
        print("")

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
def log_cash(p: Portfolio) -> None:
    print("- CASH")
    print(f"{p.cash:,.2f} USD")
    print("")


# method handles logging equities in the specified portfolio
def log_equities(p: Portfolio) -> None:
    print("- EQUITIES")
    if len(p.equities) != 0:
        print("ticker" + "\t" + "price" + "\t" + "shares" + "\t" + "ytd")
        for eq in p.equities:
            print(eq.ticker + "\t" + str(eq.price) + "\t" + str(eq.shares) + "\t" + f"{str(round(eq.ytd * 100, 2))}%")
    else:
        print("no equities in portfolio")

    print("")

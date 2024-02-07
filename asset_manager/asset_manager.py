import sys
import yaml
from datetime import datetime
from typing import Optional

from asset_manager.cli import CLI
from asset_manager.database import Database
from asset_manager.database.entities import Portfolio
from asset_manager.equity_service import YahooService
from asset_manager.portfolio_analyzer import PortfolioAnalyzer
from asset_manager.treasury_service import Fred


def main() -> None:
    # load config and configure services
    config = load_config()

    equity_service = YahooService()
    treasury_service = Fred(config)

    # establish database connection
    db = Database(
        user=config["mongodb"]["username"],
        password=config["mongodb"]["password"],
        database=config["mongodb"]["database"],
        cluster=config["mongodb"]["cluster"],
    )

    # get portfolio specified on command line
    p = retrieve_portfolio(db)
    if p is None:
        return

    print("")
    print(f"SUMMARY DATE - {datetime.today().date()}")
    print("---------------------------------")

    # construct portfolio analyzer and update details
    portfolio_analyzer = PortfolioAnalyzer(p, equity_service)
    portfolio_analyzer.analyze()
    db.save_portfolio(portfolio_analyzer.portfolio)

    # output cash
    log_cash(p)

    # output equities
    log_equities(p)

    # prompt CLI for executing portfolio commands
    portfolio_prompt = CLI(
        portfolio_analyzer=portfolio_analyzer,
        db=db,
        equity_service=equity_service,
        treasury_service=treasury_service,
    )
    portfolio_prompt.cmdloop()


def load_config() -> dict:
    """Loads app configuration stored in yml file

    Returns:
        dict: dictionary object representing the config file
    """

    with open("asset_manager/config.yml", "r") as config_file:
        return yaml.safe_load(config_file)


def retrieve_portfolio(db: Database) -> Optional[Portfolio]:
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
        print(
            "No portfolio name provided. Please enter a portfolio name from below list."
        )
        for name in portfolio_names:
            print(f"\t- {name}")

        # assign selected portfolio to portfolio
        portfolio_name = input("-> ")
        print("")

    p = db.get_portfolio_by_name(portfolio_name)

    # validate if portfolio exists and create new one if desired
    if p is None:
        create_new = input(
            f"{portfolio_name} does not exist. Would you like to create one with this name (y/n) = "
        )
        if create_new == "y":
            p = db.create_portfolio(portfolio_name)
        else:
            print("....exiting application")
            return None

    print(f"PORTFOLIO ID - {p.id}")

    return p


def log_cash(p: Portfolio) -> None:
    """Outputs cash balance of the portfolio

    Args:
        p (Portfolio): object representing the portfolio and its holdings
    """

    print("- CASH")
    print(f"{p.cash:,.2f} USD")
    print("")


def log_equities(p: Portfolio) -> None:
    """Outputs price, shares, and ytd return of the equities in the portfolio

    Args:
        p (Portfolio): object representing the portfolio and its holdings
    """

    print("- EQUITIES")
    if len(p.equities) != 0:
        print("ticker" + "\t" + "price" + "\t" + "shares" + "\t" + "ytd")
        for eq in p.equities:
            print(
                eq.ticker
                + "\t"
                + str(eq.price)
                + "\t"
                + str(eq.shares)
                + "\t"
                + f"{str(round(eq.ytd * 100, 2))}%"
            )
    else:
        print("no equities in portfolio")

    print("")

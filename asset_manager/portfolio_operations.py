from datetime import datetime

from asset_manager import equity_service
from asset_manager.entities_new import Equity, Portfolio, Trade
from asset_manager.database_new import Database


# method handles adding equity in the portfolio and database
def buy_equity(portfolio: Portfolio, ticker: str, shares: str, db: Database) -> None:
    shares = round(float(shares), 4)
    price = equity_service.get_equity_price(ticker)

    if (price * shares) > portfolio.cash:
        raise ValueError("cash balance is too low to purchase this block of assets")

    portfolio.equities.append(
        Equity(ticker=ticker, shares=shares, price=price)
    )
    portfolio.trades.append(
        Trade(ticker=ticker, price=price, shares=shares, execution_time=datetime.now())
    )
    portfolio.cash = round(portfolio.cash - (price * shares), 2)

    db.save_portfolio(portfolio)

    print(f"successfully added {ticker} to portfolio = {portfolio.name}")


# method handles removing equity from the portfolio and database
def sell_equity(portfolio: Portfolio, ticker: str, str_shares: str, db: Database) -> None:
    for equity in portfolio.equities:
        if equity.ticker == ticker:
            sell_shares = float(str_shares) if str_shares != "ALL" else equity.shares

            sell_amount = equity.price * sell_shares
            equity.shares = equity.shares - sell_shares

            if equity.shares == 0:
                portfolio.equities.remove(equity)

            portfolio.trades.append(
                Trade(ticker=ticker, price=equity.price, shares=-sell_shares, execution_time=datetime.now())
            )
            portfolio.cash += round(sell_amount, 2)

            db.save_portfolio(portfolio)


# method handles depositing amount into portfolio cash balance
def deposit(portfolio: Portfolio, deposit_amount: float, db: Database) -> None:
    portfolio.cash += deposit_amount
    db.save_portfolio(portfolio)

from asset_manager import equity_service
from asset_manager.entities_new import Equity, Portfolio
from asset_manager.database_new import Database


# method handles adding equity in the portfolio and database
def buy_equity(portfolio: Portfolio, ticker: str, shares: str, db: Database) -> None:
    shares = round(float(shares), 4)
    new_equity = Equity(ticker=ticker, shares=shares, weight=0, price=0)
    price = equity_service.get_equity_price(new_equity)

    if (price * shares) > portfolio.cash:
        raise ValueError("cash balance is too low to purchase this block of assets")

    portfolio.equities.append(new_equity)
    portfolio.cash = round(portfolio.cash - (price * shares), 2)
    db.save_portfolio(portfolio)

    print(f"successfully added {ticker} to portfolio = {portfolio.name}")


# method handles removing equity from the portfolio and database
def sell_equity(portfolio: Portfolio, ticker: str, str_shares: str, db: Database) -> None:
    sell_shares = 0
    if str_shares != "ALL":
        sell_shares = float(str_shares)

    sell_amount = 0
    for equity in portfolio.equities:
        if equity.ticker == ticker:
            if str_shares == "ALL" or sell_shares >= equity.shares:
                sell_amount = equity.price * equity.shares
                portfolio.equities.remove(equity)
            else:
                sell_amount = equity.price * sell_shares
                equity.shares = equity.shares - sell_shares

            portfolio.cash += round(sell_amount, 2)

            db.save_portfolio(portfolio)


# method handles depositing amount into portfolio cash balance
def deposit(portfolio: Portfolio, deposit_amount: float, db: Database) -> None:
    portfolio.cash += deposit_amount
    db.save_portfolio(portfolio)

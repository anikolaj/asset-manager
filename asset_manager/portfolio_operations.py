from datetime import datetime

from asset_manager import pnl
from asset_manager.entities_new import Equity, Lot, Portfolio, Trade
from asset_manager.equity_service import EquityService
from asset_manager.database_new import Database


# method handles trading the equity in the portfolio and saving to database
def trade_equity(
    portfolio: Portfolio,
    ticker: str,
    shares: float,
    db: Database,
    equity_service: EquityService,
) -> None:
    now = datetime.now()
    price, previous_day_price = equity_service.get_equity_prices(ticker)

    if (price * shares) > portfolio.cash:
        raise ValueError("cash balance is too low to purchase this block of assets")

    equity = next((eq for eq in portfolio.equities if eq.ticker == ticker), None)

    if equity is None:
        # add equity to the portfolio if not found
        portfolio.equities.append(
            Equity(
                ticker=ticker,
                shares=shares,
                price=price,
                previous_day_price=previous_day_price,
                year_start_price=equity_service.get_equity_year_start_price(ticker),
                lots=[Lot(shares=shares, price=price, execution_time=now)],
            )
        )
    else:
        # update equity shares
        equity.shares += shares
        equity.price = price

        # calculation for PnL
        pnl.calculate_pnl(shares, price, equity, portfolio)

        # if equity shares are zero, remove from portfolio
        if equity.shares == 0:
            portfolio.equities.remove(equity)

    portfolio.trades.append(
        Trade(ticker=ticker, price=price, shares=shares, execution_time=now)
    )
    portfolio.cash = round(portfolio.cash - (price * shares), 2)

    db.save_portfolio(portfolio)

    print(f"successfully added {ticker} to portfolio = {portfolio.name}")


# method handles depositing amount into portfolio cash balance
def deposit(portfolio: Portfolio, deposit_amount: float, db: Database) -> None:
    portfolio.cash += deposit_amount
    db.save_portfolio(portfolio)

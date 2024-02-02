from datetime import datetime

from asset_manager.database.entities import Equity, Lot, Portfolio


def calculate_pnl(
    shares: float, price: float, equity: Equity, portfolio: Portfolio
) -> None:
    now = datetime.now()

    # perform logic to calculate PnL
    if is_upsize(shares, equity):
        equity.lots.append(Lot(shares=shares, price=price, execution_time=now))
    else:
        current_shares = shares

        while True:
            # we have liquidated shares
            if current_shares == 0:
                break

            # we have no lots to operate on
            if len(equity.lots) == 0:
                break

            # get the head of the lot queue
            current_lot = equity.lots[0]

            # if the current lot has enough shares to offset order
            if abs(current_lot.shares) > abs(current_shares):
                pnl_shares = current_shares
                current_lot.shares += current_shares

                current_shares = 0
            # else remove the lot
            else:
                pnl_shares = -current_lot.shares
                current_shares += current_lot.shares

                equity.lots.pop(0)

            # calculate pnl
            update_realized_pnl(price, current_lot.price, pnl_shares, portfolio)


def update_realized_pnl(
    current_price: float, entry_price: float, shares: float, portfolio: Portfolio
) -> None:
    pnl = (current_price - entry_price) * -shares
    portfolio.valuation.realized_pnl += pnl


def is_upsize(shares: float, equity: Equity) -> bool:
    return len(equity.lots) == 0 or (shares * equity.lots[0].shares > 0)

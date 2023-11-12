from bson import ObjectId
from datetime import datetime

from asset_manager.entities_new import Equity, Lot, Portfolio, Valuation
from asset_manager.pnl import calculate_pnl, is_upsize, update_realized_pnl


def test_is_upsize_with_empty_lots() -> None:
    eq = get_equity(shares=0)

    shares = 1

    assert is_upsize(shares, eq) is True


def test_is_upsize_returns_true() -> None:
    eq = get_equity(shares=4, lots=[get_lot(shares=4)])

    shares = 1

    assert is_upsize(shares, eq) is True


def test_is_upsize_returns_false() -> None:
    eq = get_equity(shares=4, lots=[get_lot(shares=4)])

    shares = -1

    assert is_upsize(shares, eq) is False


def test_update_realized_pnl_buy_shares_profit() -> None:
    current_price = 2
    entry_price = 10
    shares = 4

    portfolio = get_portfolio()

    update_realized_pnl(current_price, entry_price, shares, portfolio)
    assert portfolio.valuation.realized_pnl == 42


def test_update_realized_pnl_buy_shares_loss() -> None:
    current_price = 10
    entry_price = 2
    shares = 4

    portfolio = get_portfolio()

    update_realized_pnl(current_price, entry_price, shares, portfolio)
    assert portfolio.valuation.realized_pnl == -22


def test_update_realized_pnl_sell_shares_profit() -> None:
    current_price = 9
    entry_price = 2
    shares = -4

    portfolio = get_portfolio()

    update_realized_pnl(current_price, entry_price, shares, portfolio)
    assert portfolio.valuation.realized_pnl == 38


def test_update_realized_pnl_sell_shares_loss() -> None:
    current_price = 2
    entry_price = 9
    shares = -4

    portfolio = get_portfolio()

    update_realized_pnl(current_price, entry_price, shares, portfolio)
    assert portfolio.valuation.realized_pnl == -18


# LONG POSITIONS
def test_calculate_pnl_long_upsize_empty_position() -> None:
    shares = 2
    price = 10
    equity = get_equity()
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 1


def test_calculate_pnl_long_upsize_existing_position() -> None:
    shares = 2
    price = 10
    equity = get_equity(lots=[get_lot()])
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 2


def test_calculate_pnl_long_existing_position_one_lot() -> None:
    shares = -2
    price = 12
    equity = get_equity(lots=[get_lot()])
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 1
    assert portfolio.valuation.realized_pnl == 14


def test_calculate_pnl_long_existing_position_two_lots() -> None:
    shares = -7
    price = 15
    equity = get_equity(
        lots=[
            get_lot(shares=4, price=10),
            get_lot(shares=10, price=12)
        ]
    )
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 1
    assert portfolio.valuation.realized_pnl == 39


def test_calculate_pnl_long_existing_position_multiple_lots() -> None:
    shares = -15
    price = 15
    equity = get_equity(
        lots=[
            get_lot(shares=4, price=10),
            get_lot(shares=10, price=12),
            get_lot(shares=8, price=14)
        ]
    )
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 1
    assert portfolio.valuation.realized_pnl == 61


def test_calculate_pnl_long_close_out_position() -> None:
    shares = -14
    price = 15
    equity = get_equity(
        lots=[
            get_lot(shares=4, price=10),
            get_lot(shares=10, price=12)
        ]
    )
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 0
    assert portfolio.valuation.realized_pnl == 60


# SHORT POSITIONS
def test_calculate_pnl_short_upsize_empty_position() -> None:
    shares = -2
    price = 10
    equity = get_equity(lots=[])
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 1


def test_calculate_pnl_short_upsize_existing_position() -> None:
    shares = -2
    price = 10
    equity = get_equity(shares=-4, lots=[get_lot(shares=-4)])
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 2


def test_calculate_pnl_short_existing_position_one_lot() -> None:
    shares = 2
    price = 8
    equity = get_equity(shares=-4, lots=[get_lot(shares=-4)])
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 1
    assert portfolio.valuation.realized_pnl == 14


def test_calculate_pnl_short_existing_position_two_lots() -> None:
    shares = 7
    price = 10
    equity = get_equity(
        lots=[
            get_lot(shares=-4, price=15),
            get_lot(shares=-10, price=12)
        ]
    )
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 1
    assert portfolio.valuation.realized_pnl == 36


def test_calculate_pnl_short_existing_position_multiple_lots() -> None:
    shares = 15
    price = 10
    equity = get_equity(
        lots=[
            get_lot(shares=-4, price=15),
            get_lot(shares=-10, price=12),
            get_lot(shares=-15, price=11)
        ]
    )
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 1
    assert portfolio.valuation.realized_pnl == 51


def test_calculate_pnl_short_close_out_position() -> None:
    shares = 14
    price = 10
    equity = get_equity(
        lots=[
            get_lot(shares=-4, price=15),
            get_lot(shares=-10, price=12)
        ]
    )
    portfolio = get_portfolio()

    calculate_pnl(shares, price, equity, portfolio)

    assert len(equity.lots) == 0
    assert portfolio.valuation.realized_pnl == 50


def get_portfolio() -> Portfolio:
    return Portfolio(
        id=ObjectId(),
        name="TestPortfolio",
        value=120,
        cash=100,
        equities=[
            get_equity()
        ],
        trades=[],
        valuation=(
            Valuation(
                current_value=0,
                ytd=0,
                pnl=0,
                realized_pnl=10,
                year_start_value=0,
                current_year=datetime.year
            )
        )
    )


def get_equity(
    ticker: str = "ABC",
    shares: float = 4,
    price: float = 10,
    previous_day_price: int = 10,
    lots: list[Lot] = [],
    weight: float = 1,
    year_start_price: float = 10,
    ytd: float = 0
) -> Equity:
    return Equity(
        ticker=ticker,
        shares=shares,
        price=price,
        previous_day_price=previous_day_price,
        lots=lots,
        weight=weight,
        year_start_price=year_start_price,
        ytd=ytd
    )


def get_lot(shares: float = 4, price: float = 10, execution_time: datetime = datetime.now()) -> Lot:
    return Lot(
        shares=shares,
        price=price,
        execution_time=execution_time
    )

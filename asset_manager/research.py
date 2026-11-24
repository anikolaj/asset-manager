"""Research statistics calculated from adjusted price history."""

from calendar import monthrange
from datetime import date
from math import isfinite

from tabulate import tabulate

from asset_manager.equity_service import EquityService


def calculate_annual_return(prices: dict[date, float]) -> float:
    """Calculate CAGR over the actual elapsed years of available prices."""
    observations = sorted(
        (day, price) for day, price in prices.items()
        if isfinite(price) and price > 0
    )
    if len(observations) < 2:
        raise ValueError("At least two valid closing prices are required")

    start_date, start_price = observations[0]
    end_date, end_price = observations[-1]
    years = (end_date - start_date).days / 365.25
    annual_return = (end_price / start_price) ** (1 / years) - 1
    
    if not isfinite(annual_return):
        raise ValueError("Annual return could not be calculated")
    
    return annual_return


def research(tickers: list[str], equity_service: EquityService) -> None:
    """Print annual returns using up to five years of adjusted closing prices."""
    if not tickers:
        print("No tickers provided.")
        return

    today = date.today()
    start_year = today.year - 5
    start_date = date(
        start_year, today.month,
        min(today.day, monthrange(start_year, today.month)[1]),
    )

    rows: list[tuple[str, str]] = []
    errors: list[str] = []
    for ticker in tickers:
        ticker = ticker.strip().upper()
        try:
            prices = equity_service.get_price_history(ticker, start_date, today)
            annual_return = calculate_annual_return(prices)
            rows.append((ticker, f"{annual_return:.2%}"))
        except Exception as error:
            rows.append((ticker, "N/A"))
            errors.append(f"{ticker}: {error}")

    print(tabulate(
        rows,
        headers=["Ticker", "Annual Return"],
        tablefmt="simple",
        colalign=("left", "right"),
        disable_numparse=True,
    ))

    for error in errors:
        print(error)

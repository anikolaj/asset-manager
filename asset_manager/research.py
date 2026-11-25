"""Research statistics calculated from adjusted price history."""

from calendar import monthrange
from datetime import date
from math import isfinite, sqrt
from statistics import stdev

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


def calculate_annual_volatility(prices: dict[date, float]) -> float:
    """Annualize sample volatility of daily simple returns using 252 trading days.

    Skip pairs containing invalid prices instead of bridging across them.
    """
    observations = [price for _, price in sorted(prices.items())]
    returns = []
    for i in range(1, len(observations)):
        current_price = observations[i]
        previous_price = observations[i - 1]

        if not (isfinite(previous_price) and previous_price > 0 and isfinite(current_price) and current_price > 0):
            continue

        daily_return = current_price / previous_price - 1
        if isfinite(daily_return):
            returns.append(daily_return)

    if len(returns) < 2:
        raise ValueError("At least two valid daily returns are required")

    volatility = stdev(returns) * sqrt(252)
    if not isfinite(volatility):
        raise ValueError("Annual volatility could not be calculated")

    return volatility


def calculate_maximum_drawdown(prices: dict[date, float]) -> float:
    """Return the worst peak-to-subsequent-low decline as a negative fraction."""
    observations = [
        price for _, price in sorted(prices.items())
        if isfinite(price) and price > 0
    ]
    if len(observations) < 2:
        raise ValueError("At least two valid closing prices are required")

    peak = observations[0]
    maximum_drawdown = 0.0
    for current_price in observations:
        peak = max(peak, current_price)
        drawdown = current_price / peak - 1
        maximum_drawdown = min(maximum_drawdown, drawdown)

    return maximum_drawdown


def research(tickers: list[str], equity_service: EquityService) -> None:
    """Print return, volatility, and drawdown from up to five years of adjusted daily prices."""
    if not tickers:
        print("No tickers provided.")
        return

    today = date.today()
    start_year = today.year - 5
    start_date = date(
        start_year, today.month,
        min(today.day, monthrange(start_year, today.month)[1]),
    )

    rows: list[list[str]] = []
    errors: list[str] = []
    for ticker in tickers:
        ticker = ticker.strip().upper()
        try:
            prices = equity_service.get_price_history(ticker, start_date, today)
        except Exception as error:
            rows.append([ticker, "N/A", "N/A", "N/A"])
            errors.append(f"{ticker}: {error}")
            continue

        row = [ticker]
        for name, calculate in (
            ("Annual Return", calculate_annual_return),
            ("Annual Volatility", calculate_annual_volatility),
            ("Max Drawdown", calculate_maximum_drawdown),
        ):
            try:
                row.append(f"{calculate(prices):.2%}")
            except Exception as error:
                row.append("N/A")
                errors.append(f"{ticker} - {name}: {error}")
        rows.append(row)

    print(tabulate(
        rows,
        headers=["Ticker", "Annual Return", "Annual Volatility", "Max Drawdown"],
        tablefmt="simple",
        colalign=("left", "right", "right", "right"),
        disable_numparse=True,
    ))

    for error in errors:
        print(error)

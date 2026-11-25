from datetime import date, timedelta
from math import sqrt
from unittest.mock import MagicMock

import pytest

from asset_manager.cli import CLI
from asset_manager.research import (
    calculate_annual_return,
    calculate_annual_volatility,
    calculate_maximum_drawdown,
    research,
)


@pytest.mark.parametrize("days, final_price", [(1826, 200), (180, 120), (731, 80), (365, 100)])
def test_annual_return_uses_actual_available_period(days, final_price):
    start = date(2020, 1, 1)
    # Unordered data and intermediate prices should not change the CAGR.
    prices = {
        start + timedelta(days=days): final_price,
        start + timedelta(days=10): 150,
        start: 100,
    }
    expected = (final_price / 100) ** (365.25 / days) - 1
    assert calculate_annual_return(prices) == pytest.approx(expected)


@pytest.mark.parametrize("prices", [{}, {date(2020, 1, 1): 100}])
def test_annual_return_requires_two_observations(prices):
    with pytest.raises(ValueError, match="two valid"):
        calculate_annual_return(prices)


def test_annual_return_ignores_missing_and_invalid_prices():
    start = date(2020, 1, 1)
    prices = {
        start: float("nan"),
        start + timedelta(days=1): 100,
        start + timedelta(days=2): 0,
        start + timedelta(days=3): -1,
        start + timedelta(days=1462): 200,
        start + timedelta(days=1463): float("inf"),
    }
    assert calculate_annual_return(prices) == pytest.approx(2 ** 0.25 - 1)


def test_annual_volatility_uses_sample_daily_returns_in_date_order():
    # Returns are +10%, -10%, +10%; sample variance is 0.04 / 3.
    prices = {
        date(2026, 1, 8): 108.9,
        date(2026, 1, 5): 100,
        date(2026, 1, 7): 99,
        date(2026, 1, 6): 110,
    }
    assert calculate_annual_volatility(prices) == pytest.approx(sqrt(0.04 / 3 * 252))


@pytest.mark.parametrize("values", [[100, 100, 100], [100, 110, 121]])
def test_constant_daily_returns_have_zero_volatility(values):
    start = date(2026, 1, 5)
    prices = {start + timedelta(days=i): value for i, value in enumerate(values)}
    assert calculate_annual_volatility(prices) == pytest.approx(0, abs=1e-12)


@pytest.mark.parametrize("count", [0, 1, 2])
def test_annual_volatility_requires_two_daily_returns(count):
    start = date(2026, 1, 5)
    prices = {start + timedelta(days=i): 100 + i for i in range(count)}
    with pytest.raises(ValueError, match="two valid daily returns"):
        calculate_annual_volatility(prices)


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), 0, -1])
def test_volatility_does_not_bridge_invalid_prices(invalid):
    values = [100, 110, invalid, 200, 180]
    start = date(2026, 1, 5)
    prices = {start + timedelta(days=i): value for i, value in enumerate(values)}
    # Only +10% and -10% are usable; no return spans the invalid observation.
    assert calculate_annual_volatility(prices) == pytest.approx(sqrt(0.02 * 252))


@pytest.mark.parametrize("values, expected", [
    ([100, 120, 90, 110], -0.25),
    ([100, 120, 90, 150, 90, 160], -0.40),
    ([100, 120, 150], 0),
    ([100, 100, 100], 0),
    ([100, 80, 60], -0.40),
    ([50, 100], 0),
    ([100, 50], -0.50),
])
def test_maximum_drawdown_tracks_peaks_in_date_order(values, expected):
    start = date(2026, 1, 5)
    # Insert in reverse order so the calculation must sort chronologically.
    prices = {start + timedelta(days=i): values[i] for i in reversed(range(len(values)))}
    assert calculate_maximum_drawdown(prices) == pytest.approx(expected)


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), float("-inf"), 0, -1])
def test_maximum_drawdown_ignores_invalid_prices(invalid):
    start = date(2026, 1, 5)
    prices = {start: 120, start + timedelta(days=1): invalid, start + timedelta(days=2): 90}
    assert calculate_maximum_drawdown(prices) == pytest.approx(-0.25)


@pytest.mark.parametrize("values", [[], [100], [float("nan"), 100, 0]])
def test_maximum_drawdown_requires_two_valid_prices(values):
    start = date(2026, 1, 5)
    prices = {start + timedelta(days=i): value for i, value in enumerate(values)}
    with pytest.raises(ValueError, match="two valid closing prices"):
        calculate_maximum_drawdown(prices)


def test_research_prints_all_statistics_with_one_price_fetch(capsys):
    service = MagicMock()
    start = date(2026, 1, 5)
    service.get_price_history.return_value = {
        start: 100, start + timedelta(days=1): 110, start + timedelta(days=2): 99,
    }

    research(["TEST"], equity_service=service)

    output = capsys.readouterr().out
    assert "Annual Volatility" in output
    assert "Max Drawdown" in output
    row = next(line for line in output.splitlines() if line.startswith("TEST"))
    assert row.split() == ["TEST", "-84.05%", "224.50%", "-10.00%"]
    service.get_price_history.assert_called_once()


def test_insufficient_volatility_history_preserves_annual_return(capsys):
    service = MagicMock()
    today = date.today()
    service.get_price_history.return_value = {today - timedelta(days=1461): 100, today: 200}

    research(["SHORT"], equity_service=service)

    output = capsys.readouterr().out
    row = next(line for line in output.splitlines() if line.startswith("SHORT ") and " - " not in line)
    assert row.split() == ["SHORT", "18.92%", "N/A", "0.00%"]


def test_research_prints_returns_and_continues_after_failed_ticker(capsys):
    service = MagicMock()
    today = date.today()
    service.get_price_history.side_effect = [
        RuntimeError("Price provider unavailable"),
        {},
        {today - timedelta(days=1461): 100, today: 200},
    ]

    research(["BAD", "EMPTY", "GOOD"], equity_service=service)

    output = capsys.readouterr().out
    assert "Annual Return" in output
    assert "BAD" in output and "N/A" in output
    assert "EMPTY" in output
    assert "GOOD" in output and "18.92%" in output
    assert "Price provider unavailable" in output
    for ticker in ("BAD", "EMPTY"):
        row = next(line for line in output.splitlines() if line.startswith(ticker + " ") and " - " not in line)
        assert row.split() == [ticker, "N/A", "N/A", "N/A"]
    _, start, end = service.get_price_history.call_args.args
    assert start.year == today.year - 5
    assert start.month == today.month
    assert end == today


def test_cli_research_uses_configured_equity_service(capsys):
    service = MagicMock()
    today = date.today()
    service.get_price_history.return_value = {
        today - timedelta(days=1461): 100, today: 200,
    }
    cli = CLI(MagicMock(), MagicMock(), service, MagicMock())

    cli.onecmd("research aapl, msft")

    assert [call.args[0] for call in service.get_price_history.call_args_list] == ["AAPL", "MSFT"]
    assert capsys.readouterr().out.count("18.92%") == 2

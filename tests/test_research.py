from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from asset_manager.cli import CLI
from asset_manager.research import calculate_annual_return, research


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

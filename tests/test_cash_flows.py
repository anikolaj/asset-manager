from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from bson import BSON

from asset_manager.cli import CLI
from asset_manager.cli.portfolio_operations import deposit
from asset_manager.database import CashFlow, CashFlowOperation, Database


@pytest.fixture
def db():
    database = Database.__new__(Database)
    database.db = MagicMock()
    return database


@pytest.mark.parametrize("operation", list(CashFlowOperation))
def test_cash_flows_survive_portfolio_database_round_trip(db, operation):
    portfolio = db.create_portfolio("cash flows")
    timestamp = datetime(2026, 11, 10, 12, 30)
    portfolio.cash_flows.append(CashFlow(100, timestamp, operation))

    db.save_portfolio(portfolio)

    collection = db.db.get_collection.return_value
    query, update = collection.update_one.call_args.args
    assert query == {"_id": portfolio.id}
    # Exercise BSON serialization as well as the application's conversion.
    document = BSON.encode(update["$set"]).decode()
    assert document["cashFlows"] == [{
        "amount": 100, "timestamp": timestamp, "operation": operation.value,
    }]
    collection.find_one.return_value = document

    loaded = db.get_portfolio_by_name(portfolio.name)
    assert len(loaded.cash_flows) == 1
    assert loaded.cash_flows[0].amount == 100
    assert loaded.cash_flows[0].timestamp == timestamp
    assert loaded.cash_flows[0].operation is operation


def test_old_portfolio_without_cash_flows_loads_and_can_be_saved(db):
    document = db.create_portfolio("legacy").to_dict()
    document.pop("cashFlows")
    collection = db.db.get_collection.return_value
    collection.find_one.return_value = document

    loaded = db.get_portfolio_by_name("legacy")
    assert loaded.cash_flows == []

    db.save_portfolio(loaded)
    assert collection.update_one.call_args.args[1]["$set"]["cashFlows"] == []


def test_new_portfolios_have_independent_empty_cash_flow_lists(db):
    first = db.create_portfolio("first")
    second = db.create_portfolio("second")
    assert first.to_dict()["cashFlows"] == []
    first.cash_flows.append(CashFlow(10, datetime.now(), CashFlowOperation.DEPOSIT))
    assert second.cash_flows == []


def test_deposit_saves_balance_and_appends_transaction(db):
    portfolio = db.create_portfolio("deposit")
    portfolio.cash = 50
    previous = CashFlow(10, datetime(2026, 11, 9), CashFlowOperation.WITHDRAWAL)
    portfolio.cash_flows.append(previous)
    timestamp = datetime(2026, 11, 10, 12, 30)

    with patch("asset_manager.cli.portfolio_operations.datetime") as clock:
        clock.now.return_value = timestamp
        deposit(portfolio, 125, db)

    assert portfolio.cash == 175
    assert portfolio.cash_flows[0] is previous
    assert len(portfolio.cash_flows) == 2
    document = db.db.get_collection.return_value.update_one.call_args.args[1]["$set"]
    assert document["cash"] == 175
    assert document["cashFlows"][-1] == {
        "amount": 125, "timestamp": timestamp, "operation": "DEPOSIT",
    }


@pytest.mark.parametrize("amount", [0, -1, float("nan"), float("inf"), float("-inf")])
def test_invalid_deposit_does_not_change_or_save_portfolio(db, amount):
    portfolio = db.create_portfolio("invalid deposit")
    with pytest.raises(ValueError, match="positive and finite"):
        deposit(portfolio, amount, db)

    assert portfolio.cash == 0
    assert portfolio.cash_flows == []
    db.db.get_collection.return_value.update_one.assert_not_called()


def test_cli_deposit_accepts_documented_command(db):
    portfolio = db.create_portfolio("cli")
    analyzer = MagicMock(portfolio=portfolio)
    cli = CLI(analyzer, db, MagicMock(), MagicMock())

    cli.onecmd("deposit 100")

    assert portfolio.cash == 100
    assert len(portfolio.cash_flows) == 1
    assert portfolio.cash_flows[0].operation is CashFlowOperation.DEPOSIT


@pytest.mark.parametrize("args", ["", "100 200", "abc", "-100", "nan"])
def test_cli_invalid_deposit_reports_error_without_saving(db, args, capsys):
    portfolio = db.create_portfolio("cli invalid")
    cli = CLI(MagicMock(portfolio=portfolio), db, MagicMock(), MagicMock())

    cli.onecmd(f"deposit {args}")

    assert "INVALID" in capsys.readouterr().out
    assert portfolio.cash == 0
    assert portfolio.cash_flows == []
    db.db.get_collection.return_value.update_one.assert_not_called()

import pytest
from bson import ObjectId
from datetime import datetime, timedelta

from asset_manager.asset_manager import load_config
from asset_manager.database import Database
from asset_manager.database.entities import (
    Equity,
    Historical,
    HistoricalData,
    Lot,
    Portfolio,
    Trade,
    Valuation,
)

config = load_config()


@pytest.fixture(scope="session")
def db() -> Database:
    return Database(
        user=config["mongodb"]["username"],
        password=config["mongodb"]["password"],
        database="am_test",  # NOTE - may want to consider adding this as config item
        cluster=config["mongodb"]["cluster"],
    )


@pytest.fixture(scope="module", autouse=True)
def setup_db(db: Database):
    print("setting up database")
    print(db.connection)

    # reset collections
    db.db.get_collection("portfolio").delete_many({})
    db.db.get_collection("historical").delete_many({})

    # set test collections
    db.db.get_collection("portfolio").insert_many(
        [p.to_dict() for p in get_portfolios()]
    )
    db.db.get_collection("historical").insert_many(
        [h.to_dict() for h in get_historicals()]
    )


def test_get_portfolio_names(db: Database) -> None:
    portfolio_names = db.get_portfolio_names()

    assert sorted(portfolio_names) == ["test_portfolio_1", "test_portfolio_2"]


def test_get_portfolio_by_name(db: Database) -> None:
    portfolio_name = "test_portfolio_1"

    p = db.get_portfolio_by_name(portfolio_name)

    assert p is not None
    assert p.name == portfolio_name


def test_create_portfolio(db: Database) -> None:
    portfolio_name = "test_portfolio_3"

    p = db.create_portfolio(portfolio_name)
    assert p is not None

    q = db.get_portfolio_by_name(portfolio_name)
    assert q is not None

    assert p.id == q.id


def test_save_portfolio(db: Database) -> None:
    portfolio_name = "test_portfolio_1"

    p = db.get_portfolio_by_name(portfolio_name)
    assert p is not None

    expected_cash = p.cash + 200
    p.cash += 200

    expected_realized_pnl = 789
    p.valuation.realized_pnl = expected_realized_pnl

    db.save_portfolio(p)
    q = db.get_portfolio_by_name(portfolio_name)
    assert q is not None

    assert q.cash == expected_cash
    assert q.valuation.realized_pnl == expected_realized_pnl


def test_get_historical(db: Database) -> None:
    historical = db.get_historical(ObjectId("000000000000000000000000"))

    assert historical is not None
    assert historical.name == "test_portfolio_1"


def test_save_historical(db: Database) -> None:
    historical = db.get_historical(ObjectId("000000000000000000000000"))

    old_length = len(historical.historical_data)
    historical.historical_data.append(HistoricalData(date=datetime.now(), value=100))

    db.save_historical(historical)

    new_historical = db.get_historical(ObjectId("000000000000000000000000"))

    assert len(new_historical.historical_data) == old_length + 1
    assert new_historical.historical_data[-1].value == 100


def get_portfolios() -> list[Portfolio]:
    now = datetime.now()

    p_1 = Portfolio(
        id=ObjectId("000000000000000000000000"),
        name="test_portfolio_1",
        value=30,
        cash=10,
        equities=[
            Equity(
                ticker="ABC",
                shares=2,
                price=10,
                previous_day_price=9,
                lots=[Lot(shares=2, price=8, execution_time=now)],
                weight=0.67,
                year_start_price=7,
                ytd=0.2857,
            )
        ],
        trades=[Trade(ticker="ABC", price=8, shares=2, execution_time=now)],
        valuation=Valuation(
            current_value=30,
            ytd=0.1538,
            pnl=4,
            realized_pnl=0,
            year_start_value=26,
            current_year=2024,
        ),
    )

    p_2 = Portfolio(
        id=ObjectId("000000000000000000000001"),
        name="test_portfolio_2",
        value=1060,
        cash=500,
        equities=[
            Equity(
                ticker="EFGH",
                shares=5,
                price=42,
                previous_day_price=41,
                lots=[
                    Lot(shares=2, price=60, execution_time=now - timedelta(days=1)),
                    Lot(shares=3, price=55, execution_time=now),
                ],
                weight=0.1981,
                year_start_price=70,
                ytd=-0.40,
            ),
            Equity(
                ticker="XYZ",
                shares=7,
                price=50,
                previous_day_price=48,
                lots=[
                    Lot(shares=2, price=42, execution_time=now - timedelta(days=4)),
                    Lot(shares=2, price=45, execution_time=now - timedelta(days=2)),
                    Lot(shares=2, price=44, execution_time=now),
                ],
                weight=0.3302,
                year_start_price=52,
                ytd=-0.0385,
            ),
        ],
        trades=[
            Trade(
                ticker="EFGH",
                price=62,
                shares=2,
                execution_time=now - timedelta(days=10),
            ),
            Trade(
                ticker="EFGH",
                price=70,
                shares=-2,
                execution_time=now - timedelta(days=9),
            ),
            Trade(
                ticker="XYZ", price=42, shares=2, execution_time=now - timedelta(days=4)
            ),
            Trade(
                ticker="XYZ", price=45, shares=2, execution_time=now - timedelta(days=2)
            ),
            Trade(
                ticker="EFGH",
                price=60,
                shares=2,
                execution_time=now - timedelta(days=1),
            ),
            Trade(ticker="EFGH", price=60, shares=3, execution_time=now),
            Trade(ticker="XYZ", price=44, shares=2, execution_time=now),
        ],
        valuation=Valuation(
            current_value=1060,
            ytd=0.06,
            pnl=60,
            realized_pnl=16,
            year_start_value=1000,
            current_year=2024,
        ),
    )

    return [p_1, p_2]


def get_historicals() -> list[Historical]:
    now = datetime.now()

    h_1 = Historical(
        id=ObjectId("000000000000000000000000"),
        name="test_portfolio_1",
        historical_data=[
            HistoricalData(date=now - timedelta(days=3), value=26),
            HistoricalData(date=now - timedelta(days=2), value=25),
            HistoricalData(date=now - timedelta(days=1), value=27),
            HistoricalData(date=now, value=30),
        ],
    )

    h_2 = Historical(
        id=ObjectId("000000000000000000000001"),
        name="test_portfolio_2",
        historical_data=[
            HistoricalData(date=now - timedelta(days=4), value=1000),
            HistoricalData(date=now - timedelta(days=3), value=1020),
            HistoricalData(date=now - timedelta(days=2), value=1025),
            HistoricalData(date=now - timedelta(days=1), value=1021),
            HistoricalData(date=now, value=1060),
        ],
    )

    return [h_1, h_2]

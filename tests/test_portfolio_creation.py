from copy import deepcopy
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from asset_manager.database import Database
from asset_manager.database.entities import Historical, HistoricalData
from asset_manager.portfolio_analyzer import PortfolioAnalyzer


@pytest.fixture
def db():
    """Exercise real database methods without connecting to MongoDB."""
    database = Database.__new__(Database)
    collections = {}

    def get_collection(name):
        if name not in collections:
            documents = {}
            collection = MagicMock()

            def insert_one(document):
                documents[document["_id"]] = deepcopy(document)

            def find_one(query):
                return next(
                    (deepcopy(doc) for doc in documents.values()
                     if all(doc.get(key) == value for key, value in query.items())),
                    None,
                )

            def update_one(query, update):
                document = documents[query["_id"]]
                document.update(deepcopy(update["$set"]))

            collection.insert_one.side_effect = insert_one
            collection.find_one.side_effect = find_one
            collection.update_one.side_effect = update_one
            collections[name] = collection
        return collections[name]

    database.db = MagicMock()
    database.db.get_collection.side_effect = get_collection
    return database


def test_new_portfolio_can_load_history_and_analyze(db):
    portfolio = db.create_portfolio("new portfolio")
    historical = db.get_historical(portfolio.id)
    equity_service = MagicMock()

    assert historical.id == portfolio.id
    assert historical.name == portfolio.name
    assert len(historical.historical_data) == 1
    assert historical.historical_data[0].date.date() == date.today()
    assert historical.historical_data[0].value == 0

    PortfolioAnalyzer(portfolio, historical, db, equity_service).analyze()

    saved = db.get_portfolio_by_name(portfolio.name)
    assert saved.id == portfolio.id
    assert saved.value == 0
    assert len(db.get_historical(portfolio.id).historical_data) == 1
    equity_service.get_price_history.assert_not_called()


def test_empty_history_is_initialized_during_analysis(db):
    portfolio = db.create_portfolio("empty history")
    portfolio.cash = 100
    historical = Historical(portfolio.id, portfolio.name, [])

    PortfolioAnalyzer(portfolio, historical, db, MagicMock()).analyze()

    saved = db.get_historical(portfolio.id)
    assert len(saved.historical_data) == 1
    assert saved.historical_data[0].date.date() == date.today()
    assert saved.historical_data[0].value == 100


@pytest.mark.parametrize("cash", [0, 100])
def test_portfolio_without_equities_backfills_and_does_not_duplicate_today(db, cash):
    portfolio = db.create_portfolio("no equities")
    portfolio.cash = cash
    start = date.today() - timedelta(days=3)
    historical = Historical(
        portfolio.id,
        portfolio.name,
        [HistoricalData(datetime.combine(start, datetime.min.time()), cash)],
    )
    equity_service = MagicMock()
    analyzer = PortfolioAnalyzer(portfolio, historical, db, equity_service)

    analyzer.analyze()
    analyzer.analyze()

    saved = db.get_historical(portfolio.id)
    assert [point.date.date() for point in saved.historical_data] == [
        start + timedelta(days=offset) for offset in range(4)
    ]
    assert [point.value for point in saved.historical_data] == [cash] * 4
    equity_service.get_price_history.assert_not_called()

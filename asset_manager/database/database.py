from bson import ObjectId
from datetime import date
from pymongo import MongoClient
from typing import Optional

from asset_manager.database.entities import (
    Equity,
    Historical,
    HistoricalData,
    Lot,
    Portfolio,
    Trade,
    Valuation,
)


class Database:
    def __init__(self, user: str, password: str, database: str, cluster: str) -> None:
        self.connection = f"mongodb+srv://{user}:{password}@{cluster}/{database}?retryWrites=true&w=majority"
        self.client: MongoClient = MongoClient(host=self.connection)
        self.db = self.client.get_database(database)

    def get_portfolio_names(self) -> list[str]:
        """Returns names of portfolios stored in database

        Returns:
            list[str]: list of portfolio names
        """

        portfolios = self.db.get_collection("portfolio")
        return [p["name"] for p in portfolios.find()]

    def get_portfolio_by_name(self, portfolio_name: str) -> Optional[Portfolio]:
        """Returns portfolio object stored in database

        Args:
            portfolio_name (str): name of the portfolio

        Returns:
            Optional[Portfolio]: portfolio object, returns None if no such portfolio exists
        """

        portfolios = self.db.get_collection("portfolio")
        portfolio_entity = portfolios.find_one({"name": portfolio_name})

        if portfolio_entity is None:
            return None

        equities = []
        for equity_entity in portfolio_entity["equities"]:
            equities.append(self.__convert_entity_to_equity(equity_entity))

        trades = []
        for trade_entity in portfolio_entity["trades"]:
            trades.append(self.__convert_entity_to_trade(trade_entity))

        valuation = self.__convert_entity_to_valuation(portfolio_entity["valuation"])

        return Portfolio(
            id=portfolio_entity["_id"],
            name=portfolio_entity["name"],
            value=portfolio_entity["value"],
            cash=portfolio_entity["cash"],
            equities=equities,
            trades=trades,
            valuation=valuation,
        )

    def create_portfolio(self, portfolio_name: str) -> Portfolio:
        """Creates a new portfolio with the provided name

        Args:
            portfolio_name (str): name to be used for the portfolio

        Returns:
            Portfolio: portfolio object
        """

        portfolio = Portfolio(
            id=ObjectId(),
            name=portfolio_name,
            value=0,
            cash=0,
            equities=[],
            trades=[],
            valuation=Valuation(
                current_value=0,
                ytd=0,
                pnl=0,
                realized_pnl=0,
                year_start_value=0,
                current_year=date.today().year,
            ),
        )

        portfolios = self.db.get_collection("portfolio")
        portfolios.insert_one(portfolio.to_dict())

        return portfolio

    def save_portfolio(self, portfolio: Portfolio) -> None:
        """Saves provided portfolio to the database

        Args:
            portfolio (Portfolio): portfolio object
        """

        portfolios = self.db.get_collection("portfolio")
        portfolios.update_one({"_id": portfolio.id}, {"$set": portfolio.to_dict()})

    def get_historical(self, portfolio_id: ObjectId) -> Historical:
        """Returns historical object for the portfolio stored in database

        Args:
            portfolio_id (ObjectId): id of the portfolio

        Returns:
            Historical: object containing historical values for the portfolio
        """

        historicals = self.db.get_collection("historical")
        historical_entity = historicals.find_one({"_id": portfolio_id})

        if historical_entity is None:
            raise Exception("No historical entity availabe - check database!")

        historical_data = []
        for historical_data_entity in historical_entity["historicalData"]:
            historical_data.append(
                HistoricalData(
                    date=historical_data_entity["date"],
                    value=historical_data_entity["value"],
                )
            )

        return Historical(
            id=historical_entity["_id"],
            name=historical_entity["name"],
            historical_data=historical_data,
        )

    def __convert_entity_to_equity(self, equity_entity: dict) -> Equity:
        return Equity(
            ticker=equity_entity["ticker"],
            shares=equity_entity["shares"],
            weight=equity_entity["weight"],
            price=equity_entity["price"],
            year_start_price=equity_entity["yearStartPrice"],
            ytd=equity_entity["ytd"],
            previous_day_price=equity_entity["previousDayPrice"],
            lots=[self.__convert_entity_to_lot(lot) for lot in equity_entity["lots"]],
        )

    def __convert_entity_to_trade(self, trade_entity: dict) -> Trade:
        return Trade(
            ticker=trade_entity["ticker"],
            price=trade_entity["price"],
            shares=trade_entity["shares"],
            execution_time=trade_entity["executionTime"],
        )

    def __convert_entity_to_valuation(self, valuation_entity: dict) -> Valuation:
        return Valuation(
            current_value=valuation_entity["currentValue"],
            ytd=valuation_entity["ytd"],
            pnl=valuation_entity["pnl"],
            realized_pnl=valuation_entity["realizedPnl"],
            year_start_value=valuation_entity["yearStartValue"],
            current_year=valuation_entity["currentYear"],
        )

    def __convert_entity_to_lot(self, lot_entity: dict) -> Lot:
        return Lot(
            shares=lot_entity["shares"],
            price=lot_entity["price"],
            execution_time=lot_entity["executionTime"],
        )

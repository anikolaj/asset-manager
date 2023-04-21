from bson import ObjectId
from pymongo import MongoClient

from asset_manager.entities_new import Equity, Portfolio, Trade, Valuation


class Database:
    def __init__(self, user: str, password: str, database: str, cluster: str) -> None:
        self.connection = f"mongodb+srv://{user}:{password}@{cluster}/{database}?retryWrites=true&w=majority"
        self.client = MongoClient(host=self.connection)
        self.db = self.client.get_database(database)

    def get_portfolio_by_name(self, portfolio_name: str) -> Portfolio:
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

        valuation = None
        if portfolio_entity["valuation"] is not None:
            valuation = Valuation(
                current_value=portfolio_entity["valuation"]["currentValue"],
                ytd=portfolio_entity["valuation"]["ytd"],
                pnl=portfolio_entity["valuation"]["pnl"],
                year_start_value=portfolio_entity["valuation"]["yearStartValue"],
                current_year=portfolio_entity["valuation"]["currentYear"]
            )

        portfolio = Portfolio(
            id=portfolio_entity["_id"],
            name=portfolio_entity["name"],
            value=portfolio_entity["value"],
            cash=portfolio_entity["cash"],
            equities=equities,
            trades=trades,
            valuation=valuation
        )

        return portfolio

    def create_portfolio(self, portfolio_name: str) -> Portfolio:
        portfolio = Portfolio(
            id=ObjectId(),
            name=portfolio_name,
            value=0,
            cash=0,
            equities=[],
            trades=[]
        )

        portfolios = self.db.get_collection("portfolio")
        portfolios.insert_one(portfolio.to_dict())

        return portfolio

    def save_portfolio(self, portfolio: Portfolio) -> None:
        portfolios = self.db.get_collection("portfolio")
        portfolios.update_one({"_id": portfolio.id}, {"$set": portfolio.to_dict()})

    def add_equity_to_portfolio(self, portfolio: Portfolio, new_equity: Equity) -> None:
        portfolio.equities.append(new_equity)
        portfolios = self.db.get_collection("portfolio")
        portfolios.update_one({"_id": portfolio.id}, {"$push": {"equities": new_equity.to_dict()}})

    def save_trade(self, trade: Trade) -> None:
        trades = self.db.get_collection("trades")
        trades.insert_one(trade.to_dict())

    def __convert_entity_to_equity(self, equity_entity: dict) -> Equity:
        return Equity(
            ticker=equity_entity["ticker"],
            shares=equity_entity["shares"],
            weight=equity_entity["weight"],
            price=equity_entity["price"],
            year_start_price=equity_entity["yearStartPrice"],
            ytd=equity_entity["ytd"]
        )

    def __convert_entity_to_trade(self, trade_entity: dict) -> Trade:
        return Trade(
            ticker=trade_entity["ticker"],
            price=trade_entity["price"],
            shares=trade_entity["shares"],
            execution_time=trade_entity["executionTime"]
        )

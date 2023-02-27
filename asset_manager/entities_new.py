from datetime import datetime
from typing import Optional

from bson import ObjectId


class Equity:
    def __init__(
        self,
        ticker: str,
        shares: float,
        price: float,
        weight: Optional[float] = None,
        year_start_price: Optional[float] = None,
        ytd: Optional[float] = None
    ) -> None:
        self.ticker = ticker
        self.shares = shares
        self.weight = weight
        self.price = price
        self.year_start_price = year_start_price
        self.ytd = ytd

    def to_dict(self) -> dict:
        entity = {}

        entity["ticker"] = self.ticker
        entity["shares"] = self.shares
        entity["weight"] = self.weight
        entity["price"] = self.price
        entity["yearStartPrice"] = self.year_start_price
        entity["ytd"] = self.ytd

        return entity


class Valuation:
    def __init__(self, current_value: float, ytd: float, year_start_value: float, current_year: datetime) -> None:
        self.current_value = current_value
        self.ytd = ytd
        self.year_start_value = year_start_value
        self.current_year = current_year

    def to_dict(self) -> dict:
        entity = {}

        entity["currentValue"] = self.current_value
        entity["ytd"] = self.ytd
        entity["yearStartValue"] = self.year_start_value
        entity["currentYear"] = self.current_year

        return entity


class Trade:
    def __init__(
        self,
        ticker: str,
        price: float,
        shares: float,
        execution_time: datetime
    ) -> None:
        self.ticker = ticker
        self.price = price
        self.shares = shares
        self.execution_time = execution_time

    def to_dict(self) -> dict:
        entity = {}

        entity["ticker"] = self.ticker
        entity["price"] = self.price
        entity["shares"] = self.shares
        entity["executionTime"] = self.execution_time

        return entity


class Portfolio:
    def __init__(
        self,
        id: ObjectId,
        name: str,
        value: float,
        cash: float,
        equities: list[Equity],
        trades: list[Trade],
        valuation: Optional[Valuation] = None
    ) -> None:
        self.id = id
        self.name = name
        self.value = value
        self.cash = cash
        self.equities = equities
        self.trades = trades
        self.valuation = valuation

    def to_dict(self) -> dict:
        entity = {}

        entity["_id"] = self.id
        entity["name"] = self.name
        entity["value"] = self.value
        entity["cash"] = self.cash
        entity["equities"] = [equity.to_dict() for equity in self.equities]
        entity["trades"] = [trade.to_dict() for trade in self.trades]
        entity["valuation"] = self.valuation.to_dict() if self.valuation is self.valuation is not None else None

        return entity

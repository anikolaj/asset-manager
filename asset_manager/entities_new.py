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
        return {
            "ticker": self.ticker,
            "shares": self.shares,
            "weight": self.weight,
            "price": self.price,
            "yearStartPrice": self.year_start_price,
            "ytd": self.ytd
        }


class Valuation:
    def __init__(self, current_value: float, ytd: float, year_start_value: float, current_year: datetime) -> None:
        self.current_value = current_value
        self.ytd = ytd
        self.year_start_value = year_start_value
        self.current_year = current_year

    def to_dict(self) -> dict:
        return {
            "currentValue": self.current_value,
            "ytd": self.ytd,
            "yearStartValue": self.year_start_value,
            "currentYear": self.current_year
        }


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
        return {
            "ticker": self.ticker,
            "price": self.price,
            "shares": self.shares,
            "executionTime": self.execution_time
        }


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
        return {
            "_id": self.id,
            "name": self.name,
            "value": self.value,
            "cash": self.cash,
            "equities": [equity.to_dict() for equity in self.equities],
            "trades": [trade.to_dict() for trade in self.trades],
            "valuation": self.valuation.to_dict() if self.valuation is self.valuation is not None else None
        }

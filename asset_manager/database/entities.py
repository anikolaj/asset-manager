from datetime import datetime

from bson import ObjectId


class Lot:
    def __init__(self, shares: float, price: float, execution_time: datetime) -> None:
        self.shares = shares
        self.price = price
        self.execution_time = execution_time

    def to_dict(self):
        return {
            "shares": self.shares,
            "price": self.price,
            "executionTime": self.execution_time,
        }

    def __repr__(self) -> str:
        return f"Lot(shares={self.shares}, price={self.price}, execution_time={self.execution_time})"


class Equity:
    def __init__(
        self,
        ticker: str,
        shares: float,
        price: float,
        previous_day_price: float,
        lots: list[Lot],
        weight: float = 0,
        year_start_price: float = 0,
        ytd: float = 0,
    ) -> None:
        self.ticker = ticker
        self.shares = shares
        self.weight = weight
        self.price = price
        self.year_start_price = year_start_price
        self.ytd = ytd
        self.previous_day_price = previous_day_price
        self.lots = lots

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "shares": self.shares,
            "weight": self.weight,
            "price": self.price,
            "previousDayPrice": self.previous_day_price,
            "yearStartPrice": self.year_start_price,
            "ytd": self.ytd,
            "lots": [lot.to_dict() for lot in self.lots],
        }

    def __repr__(self) -> str:
        return (
            f"Equity(ticker={self.ticker}, shares={self.shares}, "
            f"weight={self.weight}, price={self.price}, previous_day_price={self.previous_day_price}, "
            f"year_start_price={self.year_start_price}, ytd={self.ytd}, "
            f"lots={'[..]' if len(self.lots) != 0 else '[]'})"
        )


class Valuation:
    def __init__(
        self,
        current_value: float,
        ytd: float,
        pnl: float,
        realized_pnl: float,
        year_start_value: float,
        current_year: int,
    ) -> None:
        self.current_value = current_value
        self.ytd = ytd
        self.pnl = pnl
        self.realized_pnl = realized_pnl
        self.year_start_value = year_start_value
        self.current_year = current_year

    def to_dict(self) -> dict:
        return {
            "currentValue": self.current_value,
            "ytd": self.ytd,
            "pnl": self.pnl,
            "realizedPnl": self.realized_pnl,
            "yearStartValue": self.year_start_value,
            "currentYear": self.current_year,
        }

    def __repr__(self) -> str:
        return (
            f"Valuation(current_value={self.current_value}, ytd={self.ytd}, "
            f"pnl={self.pnl}, realized_pnl={self.realized_pnl}, year_start_value={self.year_start_value}, "
            f"current_year={self.current_year})"
        )


class Trade:
    def __init__(
        self, ticker: str, price: float, shares: float, execution_time: datetime
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
            "executionTime": self.execution_time,
        }

    def __repr__(self) -> str:
        return (
            f"Trade(ticker={self.ticker}, price={self.price}, "
            f"shares={self.shares}, execution_time={self.execution_time})"
        )


class Portfolio:
    def __init__(
        self,
        id: ObjectId,
        name: str,
        value: float,
        cash: float,
        equities: list[Equity],
        trades: list[Trade],
        valuation: Valuation,
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
            "valuation": self.valuation.to_dict(),
        }

    def __repr__(self) -> str:
        return (
            f"Portfolio(id={self.id}, name={self.name}, value={self.value}, cash={self.cash}, "
            f"equities={'[..]' if len(self.equities) != 0 else '[]'}, "
            f"trades={'[..]' if len(self.equities) != 0 else '[]'}), "
            f"valuation={self.valuation!r}"
        )


class HistoricalData:
    def __init__(self, date: datetime, value: float) -> None:
        self.date = date
        self.value = value

    def to_dict(self) -> dict:
        return {"date": self.date, "value": self.value}

    def __repr__(self) -> str:
        return f"HistoricalData(date={self.date.date()}, value={self.value})"


class Historical:
    def __init__(
        self, id: ObjectId, name: str, historical_data: list[HistoricalData]
    ) -> None:
        self.id = id
        self.name = name
        self.historical_data = historical_data

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "name": self.name,
            "historicalData": [
                historical_data.to_dict() for historical_data in self.historical_data
            ],
        }

    def __repr__(self) -> str:
        return (
            f"Historical(id={self.id}, name={self.name}, "
            f"historicalData={'[..]' if len(self.historical_data) != 0 else '[]'})"
        )

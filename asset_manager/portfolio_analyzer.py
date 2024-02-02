import math
import numpy as np
from collections import defaultdict
from datetime import date
from typing import Optional

import asset_manager.utilities.math_functions as mf
from asset_manager.database.entities import Portfolio, Valuation
from asset_manager.equity_service import EquityService
from asset_manager.objects import Interval, TimeSeriesDetails


class PortfolioAnalyzer:
    def __init__(self, p: Portfolio, equity_service: EquityService) -> None:
        self.portfolio = p
        self.equity_service = equity_service
        self.current_year = date.today().year

        self.ticker_to_timeseries: dict[
            str, dict[Interval, TimeSeriesDetails]
        ] = defaultdict(defaultdict)

        self.W: dict[Interval, np.ndarray] = defaultdict()
        self.M: dict[Interval, np.ndarray] = defaultdict()
        self.C: dict[Interval, np.ndarray] = defaultdict()

        self.expected_return: dict[Interval, float] = defaultdict()
        self.variance: dict[Interval, Optional[float]] = defaultdict()
        self.standard_deviation: dict[Interval, Optional[float]] = defaultdict()

        self.mvp: dict[Interval, np.ndarray] = defaultdict()

        self.a: dict[Interval, np.ndarray] = defaultdict()
        self.b: dict[Interval, np.ndarray] = defaultdict()

        self.mvl_a: dict[Interval, np.float64] = defaultdict()
        self.mvl_b: dict[Interval, np.float64] = defaultdict()
        self.mvl_c: dict[Interval, np.float64] = defaultdict()

    def analyze(self) -> None:
        """Method handles analyzing portoflio to calculate necessary metrics and feature vectors"""

        self.update_equities()
        self.update_valuation()

        for time_interval in Interval:
            # skipping five year interval
            if time_interval == Interval.FIVE_YEAR:
                continue

            # compute weight, return, and covariance features
            self.compute_features(time_interval)

            # compute expected return, variance, and minimum variance portfolios
            self.compute_expected_return(time_interval)
            self.compute_variance(time_interval)
            self.compute_minimum_variance_portfolio(time_interval)

            # compute the minimum variance line
            self.compute_minimum_variance_line(time_interval)

    def update_equities(self) -> None:
        """Method handles updating equity information"""

        if self.portfolio.equities is None:
            return

        for eq in self.portfolio.equities:
            eq.price, eq.previous_day_price = self.equity_service.get_equity_prices(
                eq.ticker
            )

            # retrieve time interval details for the stock
            self.ticker_to_timeseries[eq.ticker][
                Interval.MONTH
            ] = self.equity_service.update_equity_details(eq, Interval.MONTH)
            self.ticker_to_timeseries[eq.ticker][
                Interval.THREE_MONTH
            ] = self.equity_service.update_equity_details(eq, Interval.THREE_MONTH)
            self.ticker_to_timeseries[eq.ticker][
                Interval.SIX_MONTH
            ] = self.equity_service.update_equity_details(eq, Interval.SIX_MONTH)
            self.ticker_to_timeseries[eq.ticker][
                Interval.YEAR
            ] = self.equity_service.update_equity_details(eq, Interval.YEAR)
            # self.ticker_to_timeseries[eq.ticker][
            #     Interval.FIVE_YEAR
            # ] = self.equity_service.update_equity_details(eq, Interval.FIVE_YEAR)

            # get the year start price of the stock
            if (
                eq.year_start_price is None
                or self.current_year != self.portfolio.valuation.current_year
            ):
                eq.year_start_price = self.equity_service.get_equity_year_start_price(
                    eq.ticker
                )

            eq.ytd = (eq.price / eq.year_start_price) - 1

    def update_valuation(self) -> None:
        """Method handles updating the valuation for the retrieved portfolio"""

        if self.portfolio.valuation is None:
            self.portfolio.valuation = Valuation(
                current_value=0,
                ytd=0,
                pnl=0,
                realized_pnl=0,
                year_start_value=0,
                current_year=self.current_year,
            )
        else:
            if self.portfolio.valuation.current_year != self.current_year:
                self.portfolio.valuation.current_year = self.current_year

        self.compute_year_start_value()
        self.compute_total_value()
        self.portfolio.valuation.ytd = (
            (self.portfolio.value / self.portfolio.valuation.year_start_value) - 1
            if self.portfolio.valuation.year_start_value != 0
            else 0
        )

        ytd_percent = round(self.portfolio.valuation.ytd * 100, 2)
        pnl = self.compute_pnl()
        self.portfolio.valuation.pnl = pnl

        print(f"PORTFOLIO VALUE = {self.portfolio.value:,.2f} USD")
        print("")

        print(f"YTD = {ytd_percent}%")
        print(f"PnL (compared to previous day) = {'+' if pnl >= 0 else '-'}${abs(pnl)}")
        print("")

    def compute_total_value(self) -> None:
        """Method computes the total value of all assets in the portfolio"""

        # cash value
        total_value = self.portfolio.cash

        # equity value
        for equity in self.portfolio.equities:
            total_value += equity.shares * equity.price

        total_value = round(total_value, 2)

        self.portfolio.value = total_value
        self.portfolio.valuation.current_value = total_value

    def compute_total_value_previous_day(self) -> float:
        """Method computes the total value of all assets in the portfolio on the previous day

        Returns:
            float: previous day value of the portfolio
        """

        # cash value
        total_value = self.portfolio.cash

        # equity value
        for equity in self.portfolio.equities:
            total_value += equity.shares * equity.previous_day_price

        total_value = round(total_value, 2)

        return total_value

    def compute_year_start_value(self) -> None:
        """Method computes the year start value of all assets in the portfolio"""

        start_value = self.portfolio.cash
        for equity in self.portfolio.equities:
            start_value += equity.shares * equity.year_start_price

        start_value = round(start_value, 8)
        self.portfolio.valuation.year_start_value = start_value

    def compute_pnl(self) -> float:
        """Method handles calculating pnl for the portfolio

        Returns:
            float: pnl for portfolio compared to previous day
        """

        previous_day_total = self.compute_total_value_previous_day()
        return round(self.portfolio.value - previous_day_total, 2)

    def compute_features(self, time_interval: Interval) -> None:
        """Method calculates the feature vectors used to describe the portfolio

        Args:
            time_interval (Interval): time period to calculate the features
        """

        # print("TIME INTERVAL - " + time_interval)

        weights = []
        portfolio_returns_daily = []
        covariances: list[list[Optional[np.float64]]] = []

        for equity in self.portfolio.equities:
            daily_returns = self.ticker_to_timeseries[equity.ticker][
                time_interval
            ].returns
            daily_return = self.ticker_to_timeseries[equity.ticker][
                time_interval
            ].avg_return
            daily_risk = self.ticker_to_timeseries[equity.ticker][time_interval].std_dev

            equity.weight = (equity.shares * equity.price) / self.portfolio.value
            # print(equity.ticker + " weight = " + str(equity.weight))

            weights.append(equity.weight)
            portfolio_returns_daily.append(daily_return)

            row_covariances: list[Optional[np.float64]] = []
            no_covariance = False
            for other_equity in self.portfolio.equities:
                if equity.ticker == other_equity.ticker:
                    row_covariances.append(np.float64(1))
                else:
                    other_returns = self.ticker_to_timeseries[other_equity.ticker][
                        time_interval
                    ].returns
                    other_risk = self.ticker_to_timeseries[other_equity.ticker][
                        time_interval
                    ].std_dev

                    covariance = mf.compute_covariance_with_correlation_coefficient(
                        daily_returns, other_returns, daily_risk, other_risk
                    )
                    if covariance is None:
                        no_covariance = True
                        break

                    row_covariances.append(covariance)

            # check if we could not compute covariance for any entry in the array
            if no_covariance is True:
                covariances = []
                break

            covariances.append(row_covariances)

        self.W[time_interval] = np.array(weights)
        self.M[time_interval] = np.array(portfolio_returns_daily)
        self.C[time_interval] = np.array(covariances)

        # print("w array = " + str(self.W[time_interval]))
        # print("m array = " + str(self.M[time_interval]))
        # print("c matrix = " + str(self.C[time_interval]))

    def compute_expected_return(self, time_interval: Interval) -> None:
        """Method computes the expected return of the equities

        Args:
            time_interval (Interval): time period to calculate the expected return
        """

        self.expected_return[time_interval] = mf.calculate_expected_value(
            self.M[time_interval], self.W[time_interval]
        )

    def compute_variance(self, time_interval: Interval) -> None:
        """Method computes the variances of the equities

        Args:
            time_interval (Interval): time period to calculate the variance
        """

        variance = None
        std_dev = None

        if len(self.W[time_interval]) != 0:
            variance = mf.calculate_variance(
                self.C[time_interval], self.W[time_interval]
            )
            if variance is not None:
                std_dev = round(math.sqrt(variance), 8)

        self.variance[time_interval] = variance
        self.standard_deviation[time_interval] = std_dev

    def compute_minimum_variance_portfolio(self, time_interval: Interval) -> None:
        """Method computes the minimum variance portfolio in weights for the equities

        Args:
            time_interval (Interval): time period to calculate the minimum variance portfolio
        """

        mvp: np.ndarray = np.ndarray(0)

        if len(self.portfolio.equities) != 0 and self.C[time_interval].size != 0:
            u = np.ones(len(self.portfolio.equities))
            u_t = np.transpose(u)
            C_inv = np.linalg.inv(self.C[time_interval])

            uC_inv = u @ C_inv
            uC_invu_t = uC_inv @ u_t
            result = uC_inv / uC_invu_t

            mvp = result

        self.mvp[time_interval] = mvp

    def reweight_to_mvp(self, time_interval: Interval) -> None:
        """Method handles adjusting shares of equities to achieve the minimum variance weight

        Args:
            time_interval (Interval): time period to reweight to the minimum variance portfolio
        """

        print("reweighting portfolio")
        for i in range(0, len(self.portfolio.equities)):
            _ = self.ticker_to_timeseries[self.portfolio.equities[i].ticker]
            new_weight = self.mvp[time_interval][i]

            old_value = (
                self.portfolio.equities[i].weight * self.portfolio.equities[i].price
            )
            new_value = new_weight * self.portfolio.equities[i].price
            value_change = new_value - old_value

            self.portfolio.equities[i].shares = (
                new_weight * self.portfolio.value
            ) / self.portfolio.equities[i].price
            # NOTE - portfolio needs to be SAVED into the database
            # self.portfolio.save()

            print(
                f"{self.portfolio.equities[i].ticker} new share amount = {self.portfolio.equities[i].shares}"
            )
            print(
                f"{self.portfolio.equities[i].ticker} change in value = {value_change}"
            )

    def compute_minimum_variance_line(self, time_interval: Interval) -> None:
        """Method computes the parameters that describe the minimum variance line for the assets

        Args:
            time_interval (Interval): time period to calculate the minimum variance line
        """

        if self.C[time_interval].size == 0 or self.C[time_interval].size == 1:
            return

        u = np.ones(len(self.portfolio.equities))
        u_t = np.transpose(u)
        M_t = np.transpose(self.M[time_interval])
        C_inv = np.linalg.inv(self.C[time_interval])

        a_bar = u @ C_inv @ M_t
        b_bar = self.M[time_interval] @ C_inv @ M_t
        c_bar = u @ C_inv @ u_t

        denom = (b_bar * c_bar) - (a_bar**2)

        # w = a * m_v + b
        self.a[time_interval] = (
            ((c_bar * self.M[time_interval]) - (a_bar * u)) @ C_inv
        ) / denom
        self.b[time_interval] = (
            ((b_bar * u) - (a_bar * self.M[time_interval])) @ C_inv
        ) / denom

        # print("a parameter")
        # print(self.a[time_interval])
        # print("")
        # print("b parameter")
        # print(self.b[time_interval])

        # sigma_v = sqrt(aCa^T * m_v^2 + 2*aCb^T*m_v + bCb^T)
        a_t = np.transpose(self.a[time_interval])
        b_t = np.transpose(self.b[time_interval])

        self.mvl_a[time_interval] = self.a[time_interval] @ self.C[time_interval] @ a_t
        self.mvl_b[time_interval] = 2 * (
            self.a[time_interval] @ self.C[time_interval] @ b_t
        )
        self.mvl_c[time_interval] = self.b[time_interval] @ self.C[time_interval] @ b_t

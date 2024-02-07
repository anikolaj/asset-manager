import cmd
import os
from typing import IO

from asset_manager.cli.portfolio_operations import deposit, trade_equity
from asset_manager.database import Database
from asset_manager.equity_service import EquityService
from asset_manager.objects import Interval
from asset_manager.portfolio_analyzer import PortfolioAnalyzer
from asset_manager.treasury_service import TreasuryService
from asset_manager.utilities.excel_utility import ExcelUtility


class CLI(cmd.Cmd):
    prompt = "(asset-manager) "

    def __init__(
        self,
        portfolio_analyzer: PortfolioAnalyzer,
        db: Database,
        equity_service: EquityService,
        treasury_service: TreasuryService,
        completekey: str = "tab",
        stdin: IO[str] | None = None,
        stdout: IO[str] | None = None,
    ) -> None:
        # services
        self.portfolio_analyzer = portfolio_analyzer
        self.db = db
        self.equity_service = equity_service
        self.treasury_service = treasury_service
        self.excel_utility = ExcelUtility(self.portfolio_analyzer)

        # cli config
        super().__init__(completekey, stdin, stdout)

    def do_reweight(self, args: str) -> None:
        """
        Reweights portfolio to optimize mean variance tradeoff and recalculates statistics.

        Usage:
            reweight <time_interval>

        Parameters:
            <time_interval>: Time interval to reweight portfolio. Valid options are 1M, 3M, 6M, 1Y, or 5Y.

        Examples:
            reweight 1Y
        """
        command = args.split()

        if len(command) != 2:
            print('INVALID COMMAND FORMAT - MUST BE "REWEIGHT <TIME_INTERVAL>"')
            print("TIME_INTERVAL = 1M, 3M, 6M, 1Y, or 5Y")
            return

        time_interval = Interval(command[1])

        self.portfolio_analyzer.reweight_to_mvp(time_interval)
        self.portfolio_analyzer.compute_expected_return(time_interval)
        self.portfolio_analyzer.compute_variance(time_interval)

    def do_buy(self, args: str) -> None:
        """
        Buys the specified shares of the given ticker in the command and adds to portfolio.

        Usage:
            buy <ticker> <shares>

        Parameters:
            <ticker>: Ticker of the stock.
            <shares>: Number of shares to purchase.

        Examples:
            buy AAPL 5
        """
        command = args.split()

        if len(command) != 3:
            print('INVALID COMMAND FORMAT - MUST BE "BUY <TICKER> <SHARES>"')
            return

        ticker = command[1]
        shares = round(float(command[2]), 4)

        try:
            trade_equity(
                portfolio=self.portfolio_analyzer.portfolio,
                ticker=ticker,
                shares=shares,
                db=self.db,
                equity_service=self.equity_service,
            )
            self.portfolio_analyzer.analyze()
        except Exception as e:
            print("Exception occurred while trying to buy asset. Please view below")
            print(f"EXCEPTION - {e}")

    def do_sell(self, args: str) -> None:
        """
        Sells the specified shares of the given ticker in the command and removes from portfolio

        Note - this method allows for short selling, so shares may be negative after operation

        Usage:
            sell <ticker> <shares>

        Parameters:
            <ticker>: Ticker of the stock.
            <shares>: Number of shares to sell. 'ALL' is accepted and will sell entire position.

        Examples:
            sell AAPL 5
            sell AAPL ALL
        """
        command = args.split()

        if len(command) != 3:
            print('INVALID COMMAND FORMAT - MUST BE "SELL <TICKER> <SHARES>"')
            print('SHARES = numeric value or "ALL"')
            return

        ticker = command[1]
        shares_str = command[2]

        if shares_str == "ALL":
            equity = next(
                (
                    eq
                    for eq in self.portfolio_analyzer.portfolio.equities
                    if eq.ticker == ticker
                ),
                None,
            )

            if equity is not None:
                shares = equity.shares
            else:
                raise Exception(
                    "Equity not found in portfolio, but 'ALL' shares was specified."
                )
        else:
            shares = float(shares_str)

        shares = round(float(shares), 4)

        trade_equity(
            portfolio=self.portfolio_analyzer.portfolio,
            ticker=ticker,
            shares=-shares,
            db=self.db,
            equity_service=self.equity_service,
        )
        self.portfolio_analyzer.analyze()

    def do_deposit(self, args: str) -> None:
        """
        Deposits specified cash amount into portfolio.

        Usage:
            deposit <amount>

        Parameters:
            <amount>: Amount of cash to add to portfolio.

        Examples:
            deposit 5000
        """
        command = args.split()

        if len(command) != 2:
            print('INVALID COMMAND FORMAT - MUST BE "DEPOSIT <AMOUNT>"')
            return

        deposit_amount = float(command[1])
        deposit(
            portfolio=self.portfolio_analyzer.portfolio,
            deposit_amount=deposit_amount,
            db=self.db,
        )

    def do_rates(self, _) -> None:
        """
        Outputs US treasury rates provided by FRED

        Usage:
            rates

        Examples:
            rates
        """

        print("symbol" + "\t\t" + "rate")
        print("US 30 Year" + "\t" + str(self.treasury_service.UST30Y) + "%")
        print("US 10 Year" + "\t" + str(self.treasury_service.UST10Y) + "%")
        print("US 5 Year" + "\t" + str(self.treasury_service.UST5Y) + "%")
        print("US 1 Year" + "\t" + str(self.treasury_service.UST1Y) + "%")
        print("US 6 Month" + "\t" + str(self.treasury_service.UST6MO) + "%")
        print("US 3 Month" + "\t" + str(self.treasury_service.UST3MO) + "%")
        print("US 1 Month" + "\t" + str(self.treasury_service.UST1MO) + "%")
        print("")

    def do_export(self, _) -> None:
        """
        Exports portfolio data into an excel workbook saved in the root project directory.

        Usage:
            export

        Examples:
            export
        """

        self.excel_utility.generate_portfolio_workbook()

    def do_trades(self, command) -> None:
        """
        Outputs ten most recent trades in portfolio.

        Usage:
            trades

        Examples:
            trades
        """

        trades = sorted(
            self.portfolio_analyzer.portfolio.trades,
            key=lambda trade: trade.execution_time,
            reverse=True,
        )
        for i in range(min(len(trades), 10)):
            print(
                f"{'BUY' if trades[i].shares >= 0 else 'SELL'}"
                + "\t"
                + f"{trades[i].ticker}"
                + "\t"
                + f"{abs(trades[i].shares)} SHARES"
                + "\t"
                + f"@ ${trades[i].price}"
                + "\t"
                + f"{trades[i].execution_time}"
            )

        print("")

    def do_exit(self, _) -> bool:
        """
        Exits application.
        """

        return True

    def do_clear(self, _) -> None:
        """
        Clears terminal.
        """

        os.system("cls")

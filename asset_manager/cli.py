from asset_manager.database import Database
from asset_manager.equity_service import EquityService
from asset_manager.excel_utility import ExcelUtility
from asset_manager.objects import Interval
from asset_manager.portfolio_analyzer import PortfolioAnalyzer
from asset_manager.portfolio_operations import deposit, trade_equity
from asset_manager.treasury_service import TreasuryService


class cli:
    def __init__(
        self,
        portfolio_analyzer: PortfolioAnalyzer,
        db: Database,
        equity_service: EquityService,
        treasury_service: TreasuryService,
    ) -> None:
        self.portfolio_analyzer = portfolio_analyzer
        self.db = db
        self.equity_service = equity_service
        self.treasury_service = treasury_service

    def run_prompt(self) -> None:
        """Runs the cli prompt for the application"""

        continue_prompt = True
        while continue_prompt:
            continue_prompt = self.handle_prompt()

    def handle_prompt(self) -> bool:
        """Handles user commands and performs corresponding action

        Returns:
            bool: indicator of whether the cli should continue
        """

        portfolio_command = input("-> ").split()
        portfolio_action = portfolio_command[0]

        excel_utility = ExcelUtility(self.portfolio_analyzer)

        if portfolio_action == "REWEIGHT":
            self.reweight(portfolio_command)
        elif portfolio_action == "BUY":
            self.buy(portfolio_command)
        elif portfolio_action == "SELL":
            self.sell(portfolio_command)
        elif portfolio_action == "DEPOSIT":
            self.deposit(portfolio_command)
        elif portfolio_action == "RATES":
            self.rates()
        elif portfolio_action == "EXPORT":
            self.export(excel_utility)
        elif portfolio_action == "TRADES":
            self.trades()
        elif portfolio_action == "EXIT":
            return False
        elif portfolio_action == "HELP":
            self.help()
        else:
            print("invalid command!!! please enter a portfolio action or type HELP")

        return True

    def reweight(self, portfolio_command: list[str]) -> None:
        """Reweights portfolio to optimize mean variance tradeoff and recalculates statistics

        Args:
            portfolio_command (list[str]): list of user inputs for the command
        """

        if len(portfolio_command) != 2:
            print('INVALID COMMAND FORMAT - MUST BE "REWEIGHT [TIME_INTERVAL]"')
            print("TIME_INTERVAL = 1M, 3M, 6M, 1Y, or 5Y")
            return

        time_interval = Interval(portfolio_command[1])

        self.portfolio_analyzer.reweight_to_mvp(time_interval)
        self.portfolio_analyzer.compute_expected_return(time_interval)
        self.portfolio_analyzer.compute_variance(time_interval)

    def buy(self, portfolio_command: list[str]) -> None:
        """Buys the specified shares of the given ticker in the command and adds to portfolio

        Args:
            portfolio_command (list[str]): list of user inputs for the command
        """

        if len(portfolio_command) != 3:
            print('INVALID COMMAND FORMAT - MUST BE "BUY [TICKER] [SHARES]"')
            return

        ticker = portfolio_command[1]
        shares = round(float(portfolio_command[2]), 4)

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

    def sell(self, portfolio_command: list[str]) -> None:
        """Sells the specified shares of the given ticker in the command and removes from portfolio

        Note - this method allows for short selling, so shares may be negative after operation

        Args:
            portfolio_command (list[str]): list of user inputs for the command

        Raises:
            Exception: raises generic exception if 'ALL' shares is specified, but the ticker is not in the portfolio
        """

        if len(portfolio_command) != 3:
            print('INVALID COMMAND FORMAT - MUST BE "SELL [TICKER] [SHARES]"')
            print('SHARES = numeric value or "ALL"')
            return

        ticker = portfolio_command[1]
        shares_str = portfolio_command[2]

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

    def deposit(self, portfolio_command: list[str]) -> None:
        """Deposits specified cash amount into portfolio

        Args:
            portfolio_command (list[str]): list of user inputs for the command
        """

        if len(portfolio_command) == 2:
            deposit_amount = float(portfolio_command[1])
            deposit(
                portfolio=self.portfolio_analyzer.portfolio,
                deposit_amount=deposit_amount,
                db=self.db,
            )
        else:
            print('INVALID COMMAND FORMAT - MUST BE "DEPOSIT [AMOUNT]"')
            return

    def rates(self) -> None:
        """Outputs US treasury rates provided by FRED"""

        print("symbol" + "\t\t" + "rate")
        print("US 30 Year" + "\t" + str(self.treasury_service.UST30Y) + "%")
        print("US 10 Year" + "\t" + str(self.treasury_service.UST10Y) + "%")
        print("US 5 Year" + "\t" + str(self.treasury_service.UST5Y) + "%")
        print("US 1 Year" + "\t" + str(self.treasury_service.UST1Y) + "%")
        print("US 6 Month" + "\t" + str(self.treasury_service.UST6MO) + "%")
        print("US 3 Month" + "\t" + str(self.treasury_service.UST3MO) + "%")
        print("US 1 Month" + "\t" + str(self.treasury_service.UST1MO) + "%")
        print("")

    def export(self, excel_utility: ExcelUtility) -> None:
        """Exports portfolio data into an excel workbook saved in the root project directory

        Args:
            excel_utility (ExcelUtility): class used for writing portfolio information into an excel workbook
        """

        print("generating portfolio")
        excel_utility.generate_portfolio_workbook()
        print("")

    def trades(self) -> None:
        """Outputs ten most recent trades in portfolio"""

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

    def help(self) -> None:
        """Outputs helpful information regarding available commands for the cli"""

        print("Portfolio Commands" + "\t\t" + "Definition")
        print(
            "- BUY [TICKER] [SHARES]"
            + "\t\t"
            + "Buys SHARES for the provided TICKER. Currently supports equity tickers"
        )
        print(
            "- SELL [TICKER] [SHARES]"
            + "\t"
            + "Sells SHARES for the provided TICKER. SHARES can also be 'ALL' to indicate total sell"
        )
        print(
            "- DEPOSIT [AMOUNT]"
            + "\t\t"
            + "Adds given AMOUNT to portfolio cash balance. AMOUNT must be a decimal"
        )
        print(
            "- REWEIGHT [TIME_INTERVAL]"
            + "\t"
            + "Adjusts share amounts to achieve minimum variance portfolio for TIME_INTERVAL (daily, weekly, monthly)"
        )
        print("- RATES" + "\t\t\t\t" + "Outputs the current US Treasury rates")
        print("- EXPORT" + "\t\t\t" + "Writes portfolio data to local Excel workbook")
        print("- TRADES" + "\t\t\t" + "Outputs trade history of the portfolio")
        print("")

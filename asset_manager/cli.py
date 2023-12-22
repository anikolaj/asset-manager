import asset_manager.rates as rates
from asset_manager.database_new import Database
from asset_manager.equity_interface import EquityService
from asset_manager.excel_utility import ExcelUtility
from asset_manager.portfolio_analyzer import PortfolioAnalyzer
from asset_manager.portfolio_operations import deposit, trade_equity


class cli:
    def __init__(self, portfolio_analyzer: PortfolioAnalyzer, db: Database, equity_service: EquityService) -> None:
        self.portfolio_analyzer = portfolio_analyzer
        self.db = db
        self.equity_service = equity_service

    def run_prompt(self) -> None:
        continue_prompt = True
        while continue_prompt:
            continue_prompt = self.handle_prompt()

    def handle_prompt(self) -> bool:
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

    # ACTION = REWEIGHT
    def reweight(self, portfolio_command: str) -> None:
        if len(portfolio_command) == 2:
            time_interval = portfolio_command[1]
        else:
            print("INVALID COMMAND FORMAT - MUST BE \"REWEIGHT [TIME_INTERVAL]\"")
            print("TIME_INTERVAL = Daily, Weekly, Monthly")
            return

        self.portfolio_analyzer.reweight_to_mvp(time_interval)
        self.portfolio_analyzer.compute_expected_return(time_interval)
        self.portfolio_analyzer.compute_variance(time_interval)

    # ACTION = BUY
    def buy(self, portfolio_command: str) -> None:
        if len(portfolio_command) != 3:
            print("INVALID COMMAND FORMAT - MUST BE \"BUY [TICKER] [SHARES]\"")
            return

        ticker = portfolio_command[1]
        shares = round(float(portfolio_command[2]), 4)

        try:
            trade_equity(portfolio=self.portfolio_analyzer.portfolio, ticker=ticker, shares=shares, db=self.db, equity_service=self.equity_service)
            self.portfolio_analyzer.analyze()
        except Exception as e:
            print("Exception occurred while trying to buy asset. Please view below")
            print(f"EXCEPTION - {e}")

    # ACTION = SELL
    def sell(self, portfolio_command: str) -> None:
        if len(portfolio_command) != 3:
            print("INVALID COMMAND FORMAT - MUST BE \"SELL [TICKER] [SHARES]\"")
            print("SHARES = numeric value or \"ALL\"")
            return

        ticker = portfolio_command[1]
        shares = portfolio_command[2]

        if shares == "ALL":
            equity = next((eq for eq in self.portfolio_analyzer.portfolio.equities if eq.ticker == ticker), None)

            if equity is not None:
                shares = equity.shares
            else:
                raise Exception("Equity not found in portfolio, but 'ALL' shares was specified.")

        shares = round(float(shares), 4)

        trade_equity(portfolio=self.portfolio_analyzer.portfolio, ticker=ticker, shares=-shares, db=self.db, equity_service=self.equity_service)
        self.portfolio_analyzer.analyze()

    # ACTION = DEPOSIT
    def deposit(self, portfolio_command: str) -> None:
        if len(portfolio_command) == 2:
            deposit_amount = float(portfolio_command[1])
            deposit(portfolio=self.portfolio_analyzer.portfolio, deposit_amount=deposit_amount, db=self.db)
        else:
            print("INVALID COMMAND FORMAT - MUST BE \"DEPOSIT [AMOUNT]\"")
            return

    # ACTION = RATES
    def rates(self) -> None:
        print("symbol" + "\t\t" + "rate")
        print("US 30 Year" + "\t" + str(rates.UST30Y) + "%")
        print("US 10 Year" + "\t" + str(rates.UST10Y) + "%")
        print("US 5 Year" + "\t" + str(rates.UST5Y) + "%")
        print("US 1 Year" + "\t" + str(rates.UST1Y) + "%")
        print("US 6 Month" + "\t" + str(rates.UST6MO) + "%")
        print("US 3 Month" + "\t" + str(rates.UST3MO) + "%")
        print("US 1 Month" + "\t" + str(rates.UST1MO) + "%")
        print("")

    # ACTION = EXPORT
    def export(self, excel_utility: ExcelUtility) -> None:
        print("generating portfolio")
        excel_utility.generate_portfolio_workbook()
        print("")

    # ACTION = TRADES
    def trades(self) -> None:
        trades = sorted(self.portfolio_analyzer.portfolio.trades, key=lambda trade: trade.execution_time, reverse=True)
        for i in range(min(len(trades), 10)):
            print(f"{'BUY' if trades[i].shares >= 0 else 'SELL'} \t {trades[i].ticker} \t {abs(trades[i].shares)} SHARES \t @ ${trades[i].price} \t {trades[i].execution_time}")

        print("")

    # ACTION = HELP
    def help(self) -> None:
        print("Portfolio Commands" + "\t\t" + "Definition")
        print("- BUY [TICKER] [SHARES]" + "\t\t" + "Buys SHARES for the provided TICKER. Currently supports equity tickers")
        print("- SELL [TICKER] [SHARES]" + "\t" + "Sells SHARES for the provided TICKER. SHARES can also be 'ALL' to indicate total sell")
        print("- DEPOSIT [AMOUNT]" + "\t\t" + "Adds given AMOUNT to portfolio cash balance. AMOUNT must be a decimal")
        print("- REWEIGHT [TIME_INTERVAL]" + "\t" + "Adjusts share amounts to achieve minimum variance portfolio for TIME_INTERVAL (daily, weekly, monthly)")
        print("- RATES" + "\t\t\t\t" + "Outputs the current US Treasury rates")
        print("- EXPORT" + "\t\t\t" + "Writes portfolio data to local Excel workbook")
        print("- TRADES" + "\t\t\t" + "Outputs trade history of the portfolio")
        print("")

from asset_manager.excel_utility import ExcelUtility

class cli:

	def __init__(self, portfolio_analyzer):
		self.portfolio_analyzer = portfolio_analyzer

	# run portfolio command prompt
	def run_prompt(self):
		continue_prompt = True
		while continue_prompt:
			continue_prompt = self.handle_prompt()

	# handle user commands from portfolio prompt
	def handle_prompt(self):
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
		elif portfolio_action == "EXPORT":
			self.export(excel_utility)
		elif portfolio_action == "EXIT":
			return False
		elif portfolio_action == "HELP":
			self.help()
		else:
			print("invalid command!!! please enter a portfolio action or type HELP")

		return True

	# ACTION = REWEIGHT
	def reweight(self, portfolio_command):
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
	def buy(self, portfolio_command):
		if len(portfolio_command) == 3:
			ticker = portfolio_command[1]
			shares = portfolio_command[2]
		else:
			print("INVALID COMMAND FORMAT - MUST BE \"BUY [TICKER] [SHARES]\"")
			return

		try:
			self.portfolio_analyzer.buy_equity(ticker, shares)
			self.portfolio_analyzer.analyze()
		except Exception as e:
			print("Exception occurred while trying to buy asset. Please view below")
			print(f"EXCEPTION - {e}")

	# ACTION = SELL
	def sell(self, portfolio_command):
		if len(portfolio_command) == 3:
			ticker = portfolio_command[1]
			shares = portfolio_command[2]
		else:
			print("INVALID COMMAND FORMAT - MUST BE \"SELL [TICKER] [SHARES]\"")
			print("SHARES = numeric value or \"ALL\"")
			return

		self.portfolio_analyzer.sell_equity(ticker, shares)
		self.portfolio_analyzer.analyze()

	# ACTION = DEPOSIT
	def deposit(self, portfolio_command):
		if len(portfolio_command) == 2:
			deposit_amount = float(portfolio_command[1])
			self.portfolio_analyzer.deposit(deposit_amount)
		else:
			print("INVALID COMMAND FORMAT - MUST BE \"DEPOSIT [AMOUNT]\"")
			return

	# ACTION = EXPORT
	def export(self, excel_utility):
		excel_utility.generate_portfolio_workbook()

	# ACTION = HELP
	def help(self):
		pass
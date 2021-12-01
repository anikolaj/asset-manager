from datetime import date
import math
import numpy as np

import asset_manager.database as db
import asset_manager.math_functions as mf
import asset_manager.equity_service as equity_service
from asset_manager.entities import *

class PortfolioAnalyzer:

	# constructor
	def __init__(self, p):
		self.portfolio = p
		self.ticker_to_timeseries = {}
		for eq in p.equities:
			self.ticker_to_timeseries[eq.ticker] = {}
		
		self.W = {}
		self.M = {}
		self.C = {}
	
		self.expected_return = {}
		self.variance = {}
		self.standard_deviation = {}
	
		self.mvp = {}

		self.a = {}
		self.b = {}
		
		self.mvl_a = {}
		self.mvl_b = {}
		self.mvl_c = {}
	
	# method handles adding equity in the portfolio and database
	def buy_equity(self, ticker, shares):
		shares = round(shares, 4)
		new_equity = EquityHolding(ticker=ticker, shares=shares, weight=0, price=0)
		
		self.portfolio.equities.append(new_equity)
		self.portfolio.save()

		self.ticker_to_timeseries[ticker] = {}

		print(f"successfully added {ticker} to portfolio = {self.portfolio.name}")

	# method handles removing equity from the portfolio and database
	def sell_equity(self, ticker, str_shares):
		sell_shares = 0
		if str_shares != "ALL":
			sell_shares = float(str_shares)
		
		ticker_present = False
		for equity in self.portfolio.equities:
			if equity.ticker == ticker:
				if str_shares == "ALL" or sell_shares >= equity.shares:
					self.portfolio.equities.remove(equity)
				else:
					equity.shares = equity.shares - sell_shares

				self.portfolio.save()

	# method handles analyzing portoflio to calculate necessary metrics and feature vectors
	def analyze(self):
		# retrieve asset information
		self.update_equities()
	
		# compute portfolio total value
		self.update_valuation()

		for time_interval in ["1M", "1Q", "2Q", "1Y", "5Y"]:
			# compute features w, m, and C
			self.compute_features(time_interval)
		
			# compute expected return, variance, and minimum variance portfolios
			self.compute_expected_return(time_interval)
			self.compute_variance(time_interval)
			self.compute_minimum_variance_portfolio(time_interval)

			# compute the minimum variance line
			self.compute_minimum_variance_line(time_interval)

	# method handles updating equity information
	def update_equities(self):
		if self.portfolio.equities is None:
			return

		# equity details
		for eq in self.portfolio.equities:
			# look up equity details
			equity_details = db.get_equity_by_ticker(eq.ticker)
			
			# get current stock price
			eq.price = equity_service.get_equity_price(eq)
			
			# retrieve time interval prices for the stock
			self.ticker_to_timeseries[eq.ticker]["1M"] = equity_service.update_equity_details(eq, "1M")
			self.ticker_to_timeseries[eq.ticker]["1Q"] = equity_service.update_equity_details(eq, "1Q")
			self.ticker_to_timeseries[eq.ticker]["2Q"] = equity_service.update_equity_details(eq, "2Q")
			self.ticker_to_timeseries[eq.ticker]["1Y"] = equity_service.update_equity_details(eq, "1Y")
			self.ticker_to_timeseries[eq.ticker]["5Y"] = equity_service.update_equity_details(eq, "5Y")

			# get the year start price of the stock
			if equity_details.yearStartPrice == None:
				equity_details.yearStartPrice = equity_service.get_equity_year_start_price(equity_details)
				equity_details.save()

			eq.yearStartPrice = equity_details.yearStartPrice
	
	# method handles updating the valuation fields for the retrieved portfolio
	def update_valuation(self):
		current_year = date.today().year
		if self.portfolio.valuation == None:
			self.portfolio.valuation = Valuation(currentYear=current_year)
		else:
			if self.portfolio.valuation.currentYear != current_year:
				self.portfolio.valuation.currentYear = current_year
		
		self.compute_year_start_value()
		self.compute_total_value()
		self.portfolio.valuation.ytd = (self.portfolio.value / self.portfolio.valuation.yearStartValue) - 1
		self.portfolio.save()

		ytd_percent = round(self.portfolio.valuation.ytd * 100, 2)
		
		print(f"PORTFOLIO VALUE = {self.portfolio.value}")
		print(f"YTD = {ytd_percent}%")
		print("")
	
	# method computes the total value of all assets in the portfolio
	def compute_total_value(self):
		total_value = 0
		for equity in self.portfolio.equities:
			total_value += (equity.shares * equity.price)
	
		total_value = round(total_value, 2)
		
		self.portfolio.value = total_value
		self.portfolio.valuation.currentValue = total_value
		self.portfolio.save()
	
	# method computes the year start value of all assets in the portfolio
	def compute_year_start_value(self):
		start_value = 0
		for equity in self.portfolio.equities:
			start_value += (equity.shares * equity.yearStartPrice)

		start_value = round(start_value, 8)
		self.portfolio.valuation.yearStartValue = start_value
		self.portfolio.save()
	
	# method calculates the feature vectors used to describe the portfolio
	def compute_features(self, time_interval):
		# print("TIME INTERVAL - " + time_interval)
		
		weights = []
		portfolio_returns_daily = []
		covariances = []
		
		for equity in self.portfolio.equities:
			daily_returns = self.ticker_to_timeseries[equity.ticker][time_interval].returns
			daily_return = self.ticker_to_timeseries[equity.ticker][time_interval].avg_return
			daily_risk = self.ticker_to_timeseries[equity.ticker][time_interval].std_dev
			
			equity.weight = (equity.shares * equity.price) / self.portfolio.value
			# print(equity.ticker + " weight = " + str(equity.weight))

			weights.append(equity.weight)
			portfolio_returns_daily.append(daily_return)

			row_covariances = []
			no_covariance = False
			for other_equity in self.portfolio.equities:
				if equity.ticker == other_equity.ticker:
					row_covariances.append(1)
				else:
					other_returns = self.ticker_to_timeseries[other_equity.ticker][time_interval].returns
					other_risk = self.ticker_to_timeseries[other_equity.ticker][time_interval].std_dev
					
					covariance = mf.compute_covariance_with_correlation_coefficient(daily_returns, other_returns, daily_risk, other_risk)
					if covariance == None:
						no_covariance = True
						break
					
					row_covariances.append(covariance)
		
			# check if we could not compute covariance for any entry in the array
			if no_covariance == True:
				covariances = []
				break
			
			covariances.append(row_covariances)
		
		self.W[time_interval] = np.array(weights)
		self.M[time_interval] = np.array(portfolio_returns_daily)
		self.C[time_interval] = np.array(covariances)
		
		# print("w array = " + str(self.W[time_interval]))
		# print("m array = " + str(self.M[time_interval]))
		# print("c matrix = " + str(self.C[time_interval]))
	
	# method computes the expected return of the equities
	def compute_expected_return(self, time_interval):
		self.expected_return[time_interval] = mf.calculate_expected_value(self.M[time_interval], self.W[time_interval])
		
	# method computes the variances of the equities
	def compute_variance(self, time_interval):
		variance = None
		std_dev = None

		if len(self.W[time_interval]) != 0:
			variance = mf.calculate_variance(self.C[time_interval], self.W[time_interval])
			if variance is not None:
				std_dev = round(math.sqrt(variance), 8)

		self.variance[time_interval] = variance
		self.standard_deviation[time_interval] = std_dev
		
	# method computes the minimum variance portfolio in weights for the equities
	def compute_minimum_variance_portfolio(self, time_interval):
		mvp = []
		
		if len(self.portfolio.equities) != 0 and self.C[time_interval].size != 0:
			u = np.ones(len(self.portfolio.equities))
			u_t = np.transpose(u)
			C_inv = np.linalg.inv(self.C[time_interval])
			
			uC_inv = u @ C_inv
			uC_invu_t = uC_inv @ u_t
			result = uC_inv / uC_invu_t
			
			mvp = result.tolist()

		self.mvp[time_interval] = mvp
		
	# method handles adjusting shares of equities to achieve the minimum variance weight
	def reweight_to_mvp(self, time_interval):
		print("reweighting portfolio")
		for i in range(0, len(self.portfolio.equities)):
			equity_details_daily = self.ticker_to_timeseries[self.portfolio.equities[i].ticker]
			new_weight = self.mvp[time_interval][i]
			
			old_value = self.portfolio.equities[i].weight * self.portfolio.equities[i].price
			new_value = new_weight * self.portfolio.equities[i].price
			value_change = new_value - old_value
			
			self.portfolio.equities[i].shares = (new_weight * self.portfolio.value) / self.portfolio.equities[i].price
			self.portfolio.save()
			
			print(f"{self.portfolio.equities[i].ticker} new share amount = {self.portfolio.equities[i].shares}")
			print(f"{self.portfolio.equities[i].ticker} change in value = {value_change}")

	# method computes the parameters that describe the minimum variance line for the assets
	def compute_minimum_variance_line(self, time_interval):
		if self.C[time_interval].size == 0:
			return
		
		u = np.ones(len(self.portfolio.equities))
		u_t = np.transpose(u)
		M_t = np.transpose(self.M[time_interval])
		C_inv = np.linalg.inv(self.C[time_interval])
		
		a_bar = u @ C_inv @ M_t
		b_bar = self.M[time_interval] @ C_inv @ M_t
		c_bar = u @ C_inv @ u_t

		denom = (b_bar * c_bar) - (a_bar ** 2)
		
		# w = a * m_v + b
		self.a[time_interval] = (((c_bar * self.M[time_interval]) - (a_bar * u)) @ C_inv) / denom
		self.b[time_interval] = (((b_bar * u) - (a_bar * self.M[time_interval])) @ C_inv) / denom

		# print("a parameter")
		# print(self.a[time_interval])
		# print("")
		# print("b parameter")
		# print(self.b[time_interval])

		# sigma_v = sqrt(aCa^T * m_v^2 + 2*aCb^T*m_v + bCb^T)
		a_t = np.transpose(self.a[time_interval])
		b_t = np.transpose(self.b[time_interval])

		self.mvl_a[time_interval] = self.a[time_interval] @ self.C[time_interval] @ a_t
		self.mvl_b[time_interval] = 2 * (self.a[time_interval] @ self.C[time_interval] @ b_t)
		self.mvl_c[time_interval] = self.b[time_interval] @ self.C[time_interval] @ b_t
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
	
	# method handles adding equity in the portfolio and database
	def add_equity_to_portfolio(self, ticker, shares):
		new_equity = Equity(ticker=ticker, shares=shares, weight=0, price=0)
		
		self.portfolio.equities.append(new_equity)
		self.portfolio.save()

		print("successfully added " + ticker + " to portfolio = " + str(self.portfolio.name))

	# method handles updating equity information
	def update_equities(self):
		if self.portfolio.equities is None:
			return

		# equity daily details
		for eq in self.portfolio.equities:
			eq.price = equity_service.get_equity_price(eq)
			
			daily_equity_details = equity_service.update_equity_details(eq, "Daily")
			weekly_equity_details = equity_service.update_equity_details(eq, "Weekly")
			monthly_equity_details = equity_service.update_equity_details(eq, "Monthly")
			
			self.ticker_to_timeseries[eq.ticker]["Daily"] = daily_equity_details
			self.ticker_to_timeseries[eq.ticker]["Weekly"] = weekly_equity_details
			self.ticker_to_timeseries[eq.ticker]["Monthly"] = monthly_equity_details
	
	# method computes the total value of all assets in the portfolio
	def compute_total_value(self):
		total_value = 0
		for equity in self.portfolio.equities:
			total_value += (equity.shares * equity.price)
	
		total_value = round(total_value, 8)
		print("total portfolio value = " + str(total_value))
		
		self.portfolio.value = total_value
		self.portfolio.save()
	
	# method calculates the feature vectors used to describe the portfolio
	def compute_features(self, time_interval):
		print("TIME INTERVAL - " + time_interval)
		
		weights = []
		portfolio_returns_daily = []
		covariances = []
		
		for equity in self.portfolio.equities:
			daily_returns = self.ticker_to_timeseries[equity.ticker][time_interval].returns
			daily_return = self.ticker_to_timeseries[equity.ticker][time_interval].avg_return
			daily_risk = self.ticker_to_timeseries[equity.ticker][time_interval].std_dev
			
			equity.weight = (equity.shares * equity.price) / self.portfolio.value
			print(equity.ticker + " weight = " + str(equity.weight))

			weights.append(equity.weight)
			portfolio_returns_daily.append(daily_return)

			row_covariances = []
			for other_equity in self.portfolio.equities:
				if equity.ticker == other_equity.ticker:
					row_covariances.append(1)
				else:
					other_returns = self.ticker_to_timeseries[other_equity.ticker][time_interval].returns
					other_risk = self.ticker_to_timeseries[other_equity.ticker][time_interval].std_dev
					
					covariance = mf.compute_covariance_with_correlation_coefficient(daily_returns, other_returns, daily_risk, other_risk)
					
					row_covariances.append(covariance)
		
			covariances.append(row_covariances)
		
		self.W[time_interval] = np.array(weights)
		self.M[time_interval] = np.array(portfolio_returns_daily)
		self.C[time_interval] = np.array(covariances)
		
		print("w array = " + str(self.W[time_interval]))
		print("m array = " + str(self.M[time_interval]))
		print("c matrix = " + str(self.C[time_interval]))
	
	# method computes the expected return of the equities
	def compute_expected_return(self, time_interval):
		W_t = np.transpose(self.M[time_interval])
		result = round(np.matmul(W_t, self.M[time_interval]), 8)
		self.expected_return[time_interval] = result
		
	# method computes the variances of the equities
	def compute_variance(self, time_interval):
		variance = 0.0
		std_dev = 0.0
		
		if len(self.W[time_interval]) != 0:
			W_t = np.transpose(self.W[time_interval])
			wC = np.matmul(self.W[time_interval], self.C[time_interval])
			wCw_t = np.matmul(wC, W_t)
			variance = round(wCw_t.item(), 8)
			std_dev = round(math.sqrt(variance), 8)

		self.variance[time_interval] = variance
		self.standard_deviation[time_interval] = std_dev
		
	# method computes the minimum variance portfolio in weights for the equities
	def compute_minimum_variance_portfolio(self, time_interval):
		mvp = []
		
		if len(self.portfolio.equities) != 0:
			u = np.ones(len(self.portfolio.equities))
			C_inv = np.linalg.inv(self.C[time_interval])
			uC_inv = np.matmul(u, C_inv)
			u_t = np.transpose(u)
			uC_invu_t = np.matmul(uC_inv, u_t)
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
			
			print(self.portfolio.equities[i].ticker + " new share amount = " + str(self.portfolio.equities[i].shares))
			print(self.portfolio.equities[i].ticker + " change in value = " + str(value_change))
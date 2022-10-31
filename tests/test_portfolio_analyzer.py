import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import numpy as np

import asset_manager.database_legacy
from asset_manager.portfolio_analyzer import PortfolioAnalyzer
from asset_manager.entities_legacy import *
from asset_manager.objects import *

class TestPortfolioAnalyzer(unittest.TestCase):
	def get_portfolio(self):
		return Portfolio(name="test_portfolio", value=0)
	
	def get_equities(self):
		eq = Equity(ticker="ABC", shares=1, weight=1, price=20)
		return [eq]
	
	def get_timeseries_details(self):
		return TimeSeriesDetails(returns=[], avg_return=0.02, std_dev=0.02)
	
	def test_constructor(self):
		p = self.get_portfolio()
		portfolio_analyzer = PortfolioAnalyzer(p)
		
		self.assertEqual(portfolio_analyzer.portfolio.name, "test_portfolio")

	def test_add_equity_to_portfolio(self):
		p = self.get_portfolio()
		portfolio_analyzer = PortfolioAnalyzer(p)
		portfolio_analyzer.portfolio.save = MagicMock()
		
		portfolio_analyzer.add_equity_to_portfolio("XYZ", 1)

		self.assertEqual(len(p.equities), 1)
		portfolio_analyzer.portfolio.save.assert_called_once()

	@patch('asset_manager.portfolio_analyzer.equity_service')
	def test_update_equities(self, mock_equity_service):
		p = self.get_portfolio()
		eqs = self.get_equities()
		portfolio_analyzer = PortfolioAnalyzer(p)
		
		# verify function call returns if no equities present
		portfolio_analyzer.update_equities()
		
		# verify equities are updated if present
		portfolio_analyzer.portfolio.equities = eqs
		mock_equity_service.update_equity_details_daily = MagicMock()
		portfolio_analyzer.update_equities()

		mock_equity_service.update_equity_details_daily.assert_called_once()

	def test_compute_total_value(self):
		p = self.get_portfolio()
		eq1 = Equity(ticker="ABC", shares=1, weight=0, price=50)
		abc_details = TimeSeriesDetails(returns=[], avg_return=0.02, std_dev=0.02)
		eq2 = Equity(ticker="XYZ", shares=2, weight=0, price=20)
		xyz_details = TimeSeriesDetails(returns=[], avg_return=0.02, std_dev=0.02)
		
		p.equities = [eq1, eq2]
		portfolio_analyzer = PortfolioAnalyzer(p)
		portfolio_analyzer.portfolio.save = MagicMock()
		portfolio_analyzer.ticker_to_timeseries["ABC"] = abc_details
		portfolio_analyzer.ticker_to_timeseries["XYZ"] = xyz_details
		
		portfolio_analyzer.compute_total_value()

		self.assertEqual(portfolio_analyzer.portfolio.value, 90)

	@patch('asset_manager.portfolio_analyzer.mf')
	def test_compute_features(self, mock_mf):
		p = self.get_portfolio()

		eq1 = Equity(ticker="ABC", shares=1, weight=0, price=50)
		ts1 = TimeSeriesDetails(returns=[], avg_return=0.10, std_dev=0.10)
		
		eq2 = Equity(ticker="XYZ", shares=2, weight=0, price=20)
		ts2 = TimeSeriesDetails(returns=[], avg_return=0.20, std_dev=0.20)
		
		p.equities = [eq1, eq2]
		portfolio_analyzer = PortfolioAnalyzer(p)
		portfolio_analyzer.portfolio.save = MagicMock()
		portfolio_analyzer.ticker_to_timeseries["ABC"] = ts1
		portfolio_analyzer.ticker_to_timeseries["XYZ"] = ts2
		
		mock_mf.compute_covariance_with_correlation_coefficient.return_value = 1

		portfolio_analyzer.compute_total_value()
		portfolio_analyzer.compute_features()

		self.assertTrue(np.allclose(portfolio_analyzer.W, np.array([0.55555556, 0.44444444]), 0.00001))
		self.assertTrue(np.allclose(portfolio_analyzer.M, np.array([0.1, 0.2]), 0.00001))
		self.assertTrue(np.allclose(portfolio_analyzer.C, np.array([[0.01, 1], [1, 0.04]]), 0.00001))

	def test_compute_expected_return(self):
		p = self.get_portfolio()
		portfolio_analyzer = PortfolioAnalyzer(p)
		portfolio_analyzer.W = np.array([0.55555556, 0.44444444])
		portfolio_analyzer.M = np.array([0.1, 0.2])

		portfolio_analyzer.compute_expected_return()
		result = round(portfolio_analyzer.expected_return, 4)
		self.assertEqual(result, 0.05)

	def test_compute_variance(self):
		p = self.get_portfolio()
		portfolio_analyzer = PortfolioAnalyzer(p)
		portfolio_analyzer.W = np.array([0.55555556, 0.44444444])
		portfolio_analyzer.C = np.array([[0.01, 1], [1, 0.04]])

		portfolio_analyzer.compute_variance()
		result = round(portfolio_analyzer.standard_deviation, 4)
		self.assertEqual(result, 0.7105)

	def test_compute_minimum_variance_portfolio(self):
		p = self.get_portfolio()
		eq1 = Equity(ticker="ABC", shares=1, weight=0, price=50)
		eq2 = Equity(ticker="XYZ", shares=1, weight=0, price=20)
		p.equities = [eq1, eq2]
		
		portfolio_analyzer = PortfolioAnalyzer(p)
		
		portfolio_analyzer.C = np.array([[0.01, 1], [1, 0.04]])

		portfolio_analyzer.compute_minimum_variance_portfolio()
		self.assertTrue(np.allclose(portfolio_analyzer.mvp, np.array([0.49230769, 0.50769231]), 0.00001))

	@patch('asset_manager.portfolio_analyzer.db')
	def test_reweight_to_mvp(self, mock_db):
		p = self.get_portfolio()
		
		eq1 = Equity(ticker="ABC", shares=1, weight=0.55555556, price=50)
		ts1 = TimeSeriesDetails(returns=[], avg_return=0.10, std_dev=0.10)
		
		eq2 = Equity(ticker="XYZ", shares=2, weight=0.44444444, price=20)
		ts2 = TimeSeriesDetails(returns=[], avg_return=0.20, std_dev=0.20)
		
		p.equities = [eq1, eq2]
		
		portfolio_analyzer = PortfolioAnalyzer(p)
		portfolio_analyzer.portfolio.value = 90
		portfolio_analyzer.mvp = np.array([0.49230769, 0.50769231])

		portfolio_analyzer.portfolio.save = MagicMock()
		portfolio_analyzer.ticker_to_timeseries["ABC"] = ts1
		portfolio_analyzer.ticker_to_timeseries["XYZ"] = ts2
		
		portfolio_analyzer.reweight_to_mvp()

		abc_shares = round(portfolio_analyzer.portfolio.equities[0].shares, 5)
		xyz_shares = round(portfolio_analyzer.portfolio.equities[1].shares, 5)

		self.assertEqual(abc_shares, 0.88615)
		self.assertEqual(xyz_shares, 2.28462)
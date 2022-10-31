import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

import asset_manager.database_legacy
from asset_manager.asset_manager import launch
from asset_manager.entities_legacy import *

class TestAssetManager(unittest.TestCase):
	@patch('asset_manager.asset_manager.sys')
	@patch('asset_manager.asset_manager.db')
	@patch('builtins.input')
	@patch('asset_manager.asset_manager.PortfolioAnalyzer')
	def test_launch(self, mock_analyzer, mock_input, mock_db, mock_sys):
		mock_sys.argv = ["program", "test_portfolio"]
		
		p = Portfolio(name="test_portfolio", value=0)
		p.id = "testid123"
		eq = Equity(ticker="ABC", shares=1, weight=0, price=50)
		p.equities = [eq]
		
		mock_db.get_portfolio_by_name.return_value = p

		portfolio_analyzer = mock_analyzer.return_value
		portfolio_analyzer.update_equities = MagicMock()
		portfolio_analyzer.compute_total_value = MagicMock()
		portfolio_analyzer.compute_features = MagicMock()
		portfolio_analyzer.compute_minimum_variance_portfolio = MagicMock()
		portfolio_analyzer.reweight_to_mvp = MagicMock()
		
		mock_input.side_effect = ["y", "n"]
		
		launch()

		mock_db.get_portfolio_by_name.assert_called_once()
		portfolio_analyzer.update_equities.assert_called_once()
		portfolio_analyzer.compute_total_value.assert_called_once()
		portfolio_analyzer.compute_features.assert_called_once()
		portfolio_analyzer.compute_minimum_variance_portfolio.assert_called_once()
		portfolio_analyzer.reweight_to_mvp.assert_called_once()
		
		self.assertEqual(portfolio_analyzer.compute_expected_return.call_count, 2)
		self.assertEqual(portfolio_analyzer.compute_variance.call_count, 2)
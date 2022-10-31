import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

import asset_manager.database_legacy as db
from asset_manager.entities_legacy import *

class TestDatabase(unittest.TestCase):
	
	@patch('asset_manager.database.Portfolio')
	def test_get_portfolio_by_name(self, mock_portfolio):
		test_portfolio = Portfolio(name="test_name", value=0)
		mock_portfolio.objects.return_value.get.return_value = test_portfolio
		portfolio_entity = db.get_portfolio_by_name("test_name")
		
		self.assertEqual(portfolio_entity.name, "test_name")
		mock_portfolio.objects.return_value.get.assert_called_once()

	@patch('asset_manager.database.Portfolio')
	def test_create_portfolio(self, mock_portfolio):
		test_portfolio = Portfolio(name="test_name", value=0)
		db.create_portfolio(test_portfolio)

	def test_add_equity_to_portfolio(self):
		p = Portfolio(name="test_name", value=0)
		eq = Equity(ticker="ABC", shares=1, weight=0)
		
		p.save = MagicMock()
		p.equities.append = MagicMock()
		
		db.add_equity_to_portfolio(p, eq)

		p.equities.append.assert_called_once()
		p.save.assert_called_once()
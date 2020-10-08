import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import mock_open

import asset_manager.equity_service as equity_service
from asset_manager.entities import *

class TestEquityService(unittest.TestCase):
	
	@patch('asset_manager.equity_service.os')
	@patch('asset_manager.equity_service.requests')
	@patch('builtins.open', new_callable=mock_open)
	def test_update_equity_details_daily_existing_ticker(self, mock_o, mock_requests, mock_os):
		eq = Equity(ticker="ABC", shares=1, weight=0, price=20)
		
		mock_os.path.exists.return_value = False
		mock_requests.get.return_value.json.return_value = timeseries_sample
		
		timeseries_details = equity_service.update_equity_details_daily(eq)
		self.assertEqual(round(eq.price, 2), 78.33)
		self.verify_timeseries_details_daily(timeseries_details)

		self.assertEqual(mock_os.path.exists.call_count, 2)
		mock_os.makedirs.assert_called_once()
		mock_requests.get.return_value.json.assert_called_once()

	@patch('asset_manager.equity_service.os')
	@patch('asset_manager.equity_service.json')
	@patch('builtins.open', new_callable=mock_open)
	def test_update_equity_details_daily_new_ticker(self, mock_o, mock_json, mock_os):
		eq = Equity(ticker="ABC", shares=1, weight=0, price=20)
		
		mock_os.path.exists.return_value = True
		mock_json.load.return_value = timeseries_sample
		
		timeseries_details = equity_service.update_equity_details_daily(eq)
		self.assertEqual(round(eq.price, 2), 78.33)
		self.verify_timeseries_details_daily(timeseries_details)

		self.assertEqual(mock_os.path.exists.call_count, 2)
		mock_os.makedirs.assert_not_called()
		mock_json.load.assert_called_once()

	def verify_timeseries_details_daily(self, timeseries_details):
		self.assertEqual(round(timeseries_details.avg_return, 7), 0.0555401)
		self.assertEqual(round(timeseries_details.std_dev, 7), 0.0699202)
		rounded_returns = [ round(elem, 7) for elem in timeseries_details.returns ]
		self.assertEqual(rounded_returns, [0.0315067, -0.0118871, 0.1530389, 0.049502])

timeseries_sample = {
	"Meta Data": {
		"2. Symbol": "ABBV",
		"5. Time Zone": "US/Eastern",
		"4. Output Size": "Compact",
		"1. Information": "Daily Time Series with Splits and Dividend Events",
		"3. Last Refreshed": "2020-01-03"
	},
	"Time Series (Daily)": {
		"2019-10-28": {
			"6. volume": "7145484",
			"1. open": "76.6700",
			"5. adjusted close": "78.3300",
			"4. close": "78.3300",
			"2. high": "78.3800",
			"7. dividend amount": "0.0000",
			"8. split coefficient": "1.0000",
			"3. low": "76.4900"
		},
		"2019-08-16": {
			"6. volume": "8348143",
			"1. open": "63.5100",
			"5. adjusted close": "63.5071",
			"4. close": "64.4300",
			"2. high": "64.8100",
			"7. dividend amount": "0.0000",
			"8. split coefficient": "1.0000",
			"3. low": "63.0700"
		},
		"2019-09-30": {
			"6. volume": "8338376",
			"1. open": "74.9500",
			"5. adjusted close": "74.6354",
			"4. close": "75.7200",
			"2. high": "76.4400",
			"7. dividend amount": "0.0000",
			"8. split coefficient": "1.0000",
			"3. low": "74.9500"
		},
		"2019-08-26": {
			"6. volume": "4841405",
			"1. open": "66.4300",
			"5. adjusted close": "65.5080",
			"4. close": "66.4600",
			"2. high": "66.9300",
			"7. dividend amount": "0.0000",
			"8. split coefficient": "1.0000",
			"3. low": "66.0800"
		},
		"2019-08-27": {
			"6. volume": "7594454",
			"1. open": "66.6700",
			"5. adjusted close": "64.7293",
			"4. close": "65.6700",
			"2. high": "66.9800",
			"7. dividend amount": "0.0000",
			"8. split coefficient": "1.0000",
			"3. low": "65.4900"
		}
	}
}
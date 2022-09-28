# finnhub API constants
STOCK_QUOTE = "https://finnhub.io/api/v1/quote?symbol={}&token={}"
STOCK_DATA = "https://finnhub.io/api/v1/stock/candle?symbol={}&resolution={}&from={}&to={}&token={}"

# FRED API constants
FRED_TREASURY_RATE = "https://api.stlouisfed.org/fred/series/observations?series_id={}&file_type=json&limit=1&sort_order=desc&api_key={}"
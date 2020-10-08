from dataclasses import dataclass

@dataclass
class TimeSeriesDetails():
	returns: list
	avg_return: float
	std_dev: float

	def __init__(self, returns, avg_return, std_dev):
		self.returns = returns
		self.avg_return = avg_return
		self.std_dev = std_dev
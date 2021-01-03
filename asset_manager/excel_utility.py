import os
from openpyxl import *

class ExcelUtility:
	
	yellow_background = styles.PatternFill(fgColor=styles.colors.YELLOW, fill_type="solid")
	
	def __init__(self, portfolio_analyzer):
		self.portfolio_analyzer = portfolio_analyzer

		self.workbook = Workbook()
		self.file_name = self.portfolio_analyzer.portfolio.name + "_analysis.xlsx"
	
	def generate_portfolio_workbook(self):
		print("generating portfolio")
		self.write_summary()
		self.write_statistics()
		self.write_mvp()
		
		self.workbook.save(filename=self.file_name)

	def write_summary(self):
		summary_sheet = self.workbook.active
		summary_sheet.title = "Summary"

		sheet_title = "Portfolio Name - " + self.portfolio_analyzer.portfolio.name
		self.set_cell(summary_sheet, summary_sheet["A1"], sheet_title, True, self.yellow_background)

		# write asset details
		current_row = 3
		self.write_asset_summary(current_row, summary_sheet)
		
		# write portfolio summary
		current_row += len(self.portfolio_analyzer.portfolio.equities) + 2
		self.write_portfolio_summary(current_row, summary_sheet)

		# create border layout for summary sheet
		self.create_summary_border(summary_sheet)
	
	def write_asset_summary(self, current_row, summary_sheet):
		# set the asset summary header
		self.set_cell(summary_sheet, summary_sheet["A2"], "Asset Summary", True, None)
		self.set_cell(summary_sheet, summary_sheet["B2"], "Current", True, None)
		self.set_cell(summary_sheet, summary_sheet["C2"], "Ticker", True, None)
		self.set_cell(summary_sheet, summary_sheet["D2"], "Price", True, None)
		self.set_cell(summary_sheet, summary_sheet["E2"], "Shares", True, None)
		self.set_cell(summary_sheet, summary_sheet["F2"], "Total Value", True, None)
		self.set_cell(summary_sheet, summary_sheet["G2"], "Weight", True, None)
		
		current_row = 3
		
		for equity in self.portfolio_analyzer.portfolio.equities:
			# ticker
			self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=3), equity.ticker, False, None)
			
			# price
			self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=4), equity.price, False, None)
			
			# shares
			self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=5), equity.shares, False, None)
			
			# total value
			total_value = equity.price * equity.shares
			self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=6), total_value, False, None)
			
			# weight
			self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=7), equity.weight, False, None)
			
			current_row += 1
	
	def write_portfolio_summary(self, current_row, summary_sheet):
		# section summary
		self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=1), "Portfolio Summary", True, None)
		
		# column headers
		self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=3), "Daily", True, None)
		self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=4), "Weekly", True, None)
		self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=5), "Monthly", True, None)

		current_row += 1

		# expected return
		self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=2), "Expected Return", False, None)

		start_column = 3
		for time in ["Daily", "Weekly", "Monthly"]:
			expected_return = self.portfolio_analyzer.expected_return[time]
			self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=start_column), expected_return, False, None)

			start_column += 1

		current_row += 1
		
		# standard deviation
		self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=2), "Standard Deviation", False, None)

		start_column = 3
		for time in ["Daily", "Weekly", "Monthly"]:
			standard_deviation = self.portfolio_analyzer.standard_deviation[time]
			self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=start_column), standard_deviation, False, None)

			start_column += 1

		current_row += 2
		
		# portfolio value
		self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=1), "Total Value", True, self.yellow_background)

		portfolio_value = self.portfolio_analyzer.portfolio.value
		self.set_cell(summary_sheet, summary_sheet.cell(row=current_row, column=2), portfolio_value, True, self.yellow_background)
	
	def create_summary_border(self, summary_sheet):
		num_columns = 8
		cell_length = len(self.portfolio_analyzer.portfolio.equities) + 8
		
		# column A line for asset summary
		for i in range(1, cell_length):
			summary_sheet.cell(row=i, column=1).border = styles.borders.Border(right=styles.borders.Side(style="thin"))

		# row 2 line for asset summary
		for i in range(1, num_columns):
			cell = summary_sheet.cell(row=2, column=i)
			
			if cell.border.right.style == "thin":
				cell.border = styles.borders.Border(right=styles.borders.Side(style="thin"), bottom=styles.borders.Side(style="thin"))
			else:
				cell.border = styles.borders.Border(bottom=styles.borders.Side(style="thin"))
	
		# column G line for both summaries
		border_length = len(self.portfolio_analyzer.portfolio.equities) + 6
		for i in range(3, cell_length):
			summary_sheet.cell(row=i, column=7).border = styles.borders.Border(right=styles.borders.Side(style="thin"))
	
		# row 7 and row 10 line for portfolio summary
		portfolio_summary_start_row = len(self.portfolio_analyzer.portfolio.equities) + 5
		for i in range(1, num_columns):
			self.set_cell_border(summary_sheet.cell(row=portfolio_summary_start_row - 1, column=i))
			self.set_cell_border(summary_sheet.cell(row=cell_length - 1, column=i))
	
	def set_cell_border(self, cell):
		if cell.border.right.style == "thin":
			cell.border = styles.borders.Border(right=styles.borders.Side(style="thin"), bottom=styles.borders.Side(style="thin"))
		else:
			cell.border = styles.borders.Border(bottom=styles.borders.Side(style="thin"))
	
	def write_statistics(self):
		stats_sheet = self.workbook.create_sheet("Statistics")
		
		self.set_cell(stats_sheet, stats_sheet["A1"], "Portfolio Statistics", True, None)

		# daily statistics
		start_row = 2
		self.write_time_statistics(stats_sheet, start_row, "Daily")
		
		# weekly statistics
		start_row = start_row + len(self.portfolio_analyzer.portfolio.equities) + 2
		self.write_time_statistics(stats_sheet, start_row, "Weekly")
		
		# monthly statistics
		start_row = start_row + len(self.portfolio_analyzer.portfolio.equities) + 2
		self.write_time_statistics(stats_sheet, start_row, "Monthly")
	
	def write_mvp(self):
		mvp_sheet = self.workbook.create_sheet("MVP")
		
		self.set_cell(mvp_sheet, mvp_sheet["A1"], "Minimum Variance Portfolio", True, None)

		# daily minimum variance portfolio
		start_row = 2
		self.write_time_mvp(mvp_sheet, start_row, "Daily")
		
		# weekly minimum variance portfolio
		start_row = start_row + len(self.portfolio_analyzer.portfolio.equities) + 2
		self.write_time_mvp(mvp_sheet, start_row, "Weekly")
		
		# monthly minimum variance portfolio
		start_row = start_row + len(self.portfolio_analyzer.portfolio.equities) + 2
		self.write_time_mvp(mvp_sheet, start_row, "Monthly")

	def resize_column(self, worksheet, row, column):
		column_str = utils.get_column_letter(column)
		# this line is set because formating with a specified number format takes the original value not the formatted value
		if worksheet.cell(row, column).number_format == "General":
			if worksheet.column_dimensions[column_str].width < len(str(worksheet.cell(row, column).value)):
				worksheet.column_dimensions[column_str].width = len(str(worksheet.cell(row, column).value))

	def write_time_statistics(self, worksheet, current_row, time_interval):
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=2), time_interval, True, None)

		current_row += 1
		
		self.write_ticker_statistics(worksheet, current_row, time_interval)
		self.write_correlation_matrix(worksheet, current_row, time_interval)
		
	def write_ticker_statistics(self, worksheet, current_row, time_interval):
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=3), "Ticker", True, None)
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=4), "Expected Return", True, None)
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=5), "Standard Deviation", True, None)

		ticker_row = current_row + 1
		
		for eq in self.portfolio_analyzer.portfolio.equities:
			# ticker
			self.set_cell(worksheet, worksheet.cell(row=ticker_row, column=3), eq.ticker, False, None)

			# expected return
			expected_return = self.portfolio_analyzer.ticker_to_timeseries[eq.ticker][time_interval].avg_return
			self.set_cell(worksheet, worksheet.cell(row=ticker_row, column=4), expected_return, False, None, "0.0000000000")

			# standard deviation
			std_dev = self.portfolio_analyzer.ticker_to_timeseries[eq.ticker][time_interval].std_dev
			self.set_cell(worksheet, worksheet.cell(row=ticker_row, column=5), std_dev, False, None, "0.0000000000")

			ticker_row += 1

	def write_correlation_matrix(self, worksheet, current_row, time_interval):
		start_column = 7
		current_column = start_column
		
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=current_column), "Correlation Matrix", True, None)

		# write top row of correlation matrix
		current_column += 2
		
		for eq in self.portfolio_analyzer.portfolio.equities:
			self.set_cell(worksheet, worksheet.cell(row=current_row, column=current_column), eq.ticker, False, None)
			worksheet.cell(row=current_row, column=current_column).border = styles.borders.Border(bottom=styles.borders.Side(style="thin"))

			current_column += 1

		# write column and values of correlation matrix
		current_column = start_column + 1
		
		for i in range(0, len(self.portfolio_analyzer.portfolio.equities)):
			current_row += 1
			current_equity = self.portfolio_analyzer.portfolio.equities[i]
			
			self.set_cell(worksheet, worksheet.cell(row=current_row, column=current_column), current_equity.ticker, False, None)
			worksheet.cell(row=current_row, column=current_column).border = styles.borders.Border(right=styles.borders.Side(style="thin"))

			# write correlation coefficients into matrix
			for j in range(0, len(self.portfolio_analyzer.portfolio.equities)):
				current_column += 1
				correlation_coefficient = self.portfolio_analyzer.C[time_interval][i, j]
				self.set_cell(worksheet, worksheet.cell(row=current_row, column=current_column), correlation_coefficient, False, None, "0.00000")

				if j == (len(self.portfolio_analyzer.portfolio.equities) - 1):
					worksheet.cell(row=current_row, column=current_column + 1).border = styles.borders.Border(left=styles.borders.Side(style="thin"))

				if i == (len(self.portfolio_analyzer.portfolio.equities) - 1):
					worksheet.cell(row=current_row + 1, column=current_column).border = styles.borders.Border(top=styles.borders.Side(style="thin"))

			current_column = start_column + 1

	def write_time_mvp(self, worksheet, current_row, time_interval):
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=2), time_interval, True, None)

		current_row += 1
		
		self.write_ticker_mvp(worksheet, current_row, time_interval)

	def write_ticker_mvp(self, worksheet, current_row, time_interval):
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=3), "Ticker", True, None)
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=4), "Weight", True, None)
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=5), "Shares", True, None)
		self.set_cell(worksheet, worksheet.cell(row=current_row, column=6), "Value Change", True, None)

		ticker_row = current_row + 1
		
		for i in range(0, len(self.portfolio_analyzer.portfolio.equities)):
			current_row += 1
			current_equity = self.portfolio_analyzer.portfolio.equities[i]

			# ticker
			self.set_cell(worksheet, worksheet.cell(row=current_row, column=3), current_equity.ticker, False, None)

			# weight
			mvp_weight = self.portfolio_analyzer.mvp[time_interval][i]
			self.set_cell(worksheet, worksheet.cell(row=current_row, column=4), mvp_weight, False, None)

			# shares
			mvp_shares = (mvp_weight * self.portfolio_analyzer.portfolio.value) / current_equity.price
			self.set_cell(worksheet, worksheet.cell(row=current_row, column=5), mvp_shares, False, None)

			# value change
			new_value = mvp_shares * current_equity.price
			old_value = current_equity.shares * current_equity.price
			value_change = new_value - old_value
			self.set_cell(worksheet, worksheet.cell(row=current_row, column=6), value_change, False, None)

	def set_cell(self, sheet, cell, value, bold, fill, number_format=None):
		cell.value = value
		
		if bold == True:
			cell.font = styles.Font(bold=True)
		
		if fill is not None:
			cell.fill = fill

		if number_format is not None:
			cell.number_format = number_format

		self.resize_column(sheet, cell.row, cell.column)
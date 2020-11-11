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

		summary_sheet["A1"] = "Portfolio Name - " + self.portfolio_analyzer.portfolio.name
		summary_sheet["A1"].font = styles.Font(bold=True)
		summary_sheet["A1"].fill = self.yellow_background
		self.resize_column(summary_sheet, 1, 1)

		# write asset details
		current_row = 3
		self.write_asset_summary(current_row, summary_sheet)
		
		# write portfolio summary
		current_row += len(self.portfolio_analyzer.portfolio.equities) + 2
		self.write_portfolio_summary(current_row, summary_sheet)

		# create border layout for summary sheet
		self.create_summary_border(summary_sheet)
	
	def write_asset_summary(self, current_row, summary_sheet):
		summary_sheet["A2"] = "Asset Summary"
		summary_sheet["A2"].font = styles.Font(bold=True)
		self.resize_column(summary_sheet, 1, 1)
		
		summary_sheet["B2"] = "Current"
		summary_sheet["B2"].font = styles.Font(bold=True)
		self.resize_column(summary_sheet, 2, 2)
		
		summary_sheet["C2"] = "Ticker"
		summary_sheet["C2"].font = styles.Font(bold=True)
		self.resize_column(summary_sheet, 2, 3)
		
		summary_sheet["D2"] = "Price"
		summary_sheet["D2"].font = styles.Font(bold=True)
		self.resize_column(summary_sheet, 2, 4)
		
		summary_sheet["E2"] = "Shares"
		summary_sheet["E2"].font = styles.Font(bold=True)
		self.resize_column(summary_sheet, 2, 5)
		
		summary_sheet["F2"] = "Total Value"
		summary_sheet["F2"].font = styles.Font(bold=True)
		self.resize_column(summary_sheet, 2, 6)
		
		summary_sheet["G2"] = "Weight"
		summary_sheet["G2"].font = styles.Font(bold=True)
		self.resize_column(summary_sheet, 2, 7)
		
		current_row = 3
		
		for equity in self.portfolio_analyzer.portfolio.equities:
			summary_sheet.cell(row=current_row, column=3).value = equity.ticker
			self.resize_column(summary_sheet, current_row, 3)
			
			summary_sheet.cell(row=current_row, column=4).value = equity.price
			self.resize_column(summary_sheet, current_row, 4)
			
			summary_sheet.cell(row=current_row, column=5).value = equity.shares
			self.resize_column(summary_sheet, current_row, 5)
			
			summary_sheet.cell(row=current_row, column=6).value = equity.price * equity.shares
			self.resize_column(summary_sheet, current_row, 6)
			
			summary_sheet.cell(row=current_row, column=7).value = equity.weight
			self.resize_column(summary_sheet, current_row, 7)
			
			current_row += 1
	
	def write_portfolio_summary(self, current_row, summary_sheet):
		# section summary
		summary_sheet.cell(row=current_row, column=1).value = "Portfolio Summary"
		summary_sheet.cell(row=current_row, column=1).font = styles.Font(bold=True)
		self.resize_column(summary_sheet, current_row, 1)
		
		# column headers
		summary_sheet.cell(row=current_row, column=3).value = "Daily"
		summary_sheet.cell(row=current_row, column=3).font = styles.Font(bold=True)
		self.resize_column(summary_sheet, current_row, 3)

		summary_sheet.cell(row=current_row, column=4).value = "Weekly"
		summary_sheet.cell(row=current_row, column=4).font = styles.Font(bold=True)
		self.resize_column(summary_sheet, current_row, 4)

		summary_sheet.cell(row=current_row, column=5).value = "Monthly"
		summary_sheet.cell(row=current_row, column=5).font = styles.Font(bold=True)
		self.resize_column(summary_sheet, current_row, 5)

		current_row += 1

		# expected return
		summary_sheet.cell(row=current_row, column=2).value = "Expected Return"
		self.resize_column(summary_sheet, current_row, 2)

		start_column = 3
		for time in ["Daily", "Weekly", "Monthly"]:
			summary_sheet.cell(row=current_row, column=start_column).value = self.portfolio_analyzer.expected_return[time]
			self.resize_column(summary_sheet, current_row, 2)

			start_column += 1

		current_row += 1
		
		# standard deviation
		summary_sheet.cell(row=current_row, column=2).value = "Standard Deviation"
		self.resize_column(summary_sheet, current_row, 2)

		start_column = 3
		for time in ["Daily", "Weekly", "Monthly"]:
			summary_sheet.cell(row=current_row, column=start_column).value = self.portfolio_analyzer.standard_deviation[time]
			self.resize_column(summary_sheet, current_row, 2)

			start_column += 1

		current_row += 2
		
		# portfolio value
		summary_sheet.cell(row=current_row, column=1).value = "Total Value"
		summary_sheet.cell(row=current_row, column=1).font = styles.Font(bold=True)
		summary_sheet.cell(row=current_row, column=1).fill = self.yellow_background
		self.resize_column(summary_sheet, current_row, 1)

		summary_sheet.cell(row=current_row, column=2).value = self.portfolio_analyzer.portfolio.value
		summary_sheet.cell(row=current_row, column=2).font = styles.Font(bold=True)
		summary_sheet.cell(row=current_row, column=2).fill = self.yellow_background
		self.resize_column(summary_sheet, current_row, 2)
	
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
		
		stats_sheet["A1"] = "Portfolio Statistics"
		stats_sheet["A1"].font = styles.Font(bold=True)
		self.resize_column(stats_sheet, 1, 1)

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
		stats_sheet = self.workbook.create_sheet("MVP")
		
		stats_sheet["A1"] = "Minimum Variance Portfolio"
		stats_sheet["A1"].font = styles.Font(bold=True)
		self.resize_column(stats_sheet, 1, 1)

		# daily minimum variance portfolio
		start_row = 2
		self.write_time_mvp(stats_sheet, start_row, "Daily")
		
		# weekly minimum variance portfolio
		start_row = start_row + len(self.portfolio_analyzer.portfolio.equities) + 2
		self.write_time_mvp(stats_sheet, start_row, "Weekly")
		
		# monthly minimum variance portfolio
		start_row = start_row + len(self.portfolio_analyzer.portfolio.equities) + 2
		self.write_time_mvp(stats_sheet, start_row, "Monthly")

	def resize_column(self, worksheet, row, column):
		column_str = utils.get_column_letter(column)
		if worksheet.column_dimensions[column_str].width < len(str(worksheet.cell(row, column).value)):
			worksheet.column_dimensions[column_str].width = len(str(worksheet.cell(row, column).value))

	def write_time_statistics(self, worksheet, current_row, time_interval):
		worksheet.cell(row=current_row, column=2).value = time_interval
		worksheet.cell(row=current_row, column=2).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 2)

		current_row += 1
		
		self.write_ticker_statistics(worksheet, current_row, time_interval)
		self.write_correlation_matrix(worksheet, current_row, time_interval)
		
	def write_ticker_statistics(self, worksheet, current_row, time_interval):
		worksheet.cell(row=current_row, column=3).value = "Ticker"
		worksheet.cell(row=current_row, column=3).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 3)

		worksheet.cell(row=current_row, column=4).value = "Expected Return"
		worksheet.cell(row=current_row, column=4).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 4)

		worksheet.cell(row=current_row, column=5).value = "Standard Deviation"
		worksheet.cell(row=current_row, column=5).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 5)

		ticker_row = current_row + 1
		
		for eq in self.portfolio_analyzer.portfolio.equities:
			# ticker
			worksheet.cell(row=ticker_row, column=3).value = eq.ticker
			self.resize_column(worksheet, ticker_row, 3)

			# expected return
			worksheet.cell(row=ticker_row, column=4).value = self.portfolio_analyzer.ticker_to_timeseries[eq.ticker][time_interval].avg_return
			self.resize_column(worksheet, ticker_row, 4)

			# standard deviation
			worksheet.cell(row=ticker_row, column=5).value = self.portfolio_analyzer.ticker_to_timeseries[eq.ticker][time_interval].std_dev
			self.resize_column(worksheet, ticker_row, 5)

			ticker_row += 1

	def write_correlation_matrix(self, worksheet, current_row, time_interval):
		start_column = 7
		current_column = start_column
		
		worksheet.cell(row=current_row, column=current_column).value = "Correlation Matrix"
		worksheet.cell(row=current_row, column=current_column).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, current_column)

		# write top row of correlation matrix
		current_column += 2
		
		for eq in self.portfolio_analyzer.portfolio.equities:
			worksheet.cell(row=current_row, column=current_column).value = eq.ticker
			worksheet.cell(row=current_row, column=current_column).border = styles.borders.Border(bottom=styles.borders.Side(style="thin"))
			self.resize_column(worksheet, current_row, current_column)

			current_column += 1

		# write column and values of correlation matrix
		current_column = start_column + 1
		
		for i in range(0, len(self.portfolio_analyzer.portfolio.equities)):
			current_row += 1
			current_equity = self.portfolio_analyzer.portfolio.equities[i]
			
			worksheet.cell(row=current_row, column=current_column).value = current_equity.ticker
			worksheet.cell(row=current_row, column=current_column).border = styles.borders.Border(right=styles.borders.Side(style="thin"))
			self.resize_column(worksheet, current_row, current_column)

			# write correlation coefficients into matrix
			for j in range(0, len(self.portfolio_analyzer.portfolio.equities)):
				current_column += 1
				correlation_coefficient = self.portfolio_analyzer.C[time_interval][i, j]

				worksheet.cell(row=current_row, column=current_column).value = correlation_coefficient
				# self.resize_column(worksheet, current_row, current_column)

				if j == (len(self.portfolio_analyzer.portfolio.equities) - 1):
					worksheet.cell(row=current_row, column=current_column + 1).border = styles.borders.Border(left=styles.borders.Side(style="thin"))

				if i == (len(self.portfolio_analyzer.portfolio.equities) - 1):
					worksheet.cell(row=current_row + 1, column=current_column).border = styles.borders.Border(top=styles.borders.Side(style="thin"))

			current_column = start_column + 1

	def write_time_mvp(self, worksheet, current_row, time_interval):
		worksheet.cell(row=current_row, column=2).value = time_interval
		worksheet.cell(row=current_row, column=2).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 2)

		current_row += 1
		
		self.write_ticker_mvp(worksheet, current_row, time_interval)

	def write_ticker_mvp(self, worksheet, current_row, time_interval):
		worksheet.cell(row=current_row, column=3).value = "Ticker"
		worksheet.cell(row=current_row, column=3).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 3)

		worksheet.cell(row=current_row, column=4).value = "Weight"
		worksheet.cell(row=current_row, column=4).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 4)

		worksheet.cell(row=current_row, column=5).value = "Shares"
		worksheet.cell(row=current_row, column=5).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 5)

		worksheet.cell(row=current_row, column=6).value = "Value Change"
		worksheet.cell(row=current_row, column=6).font = styles.Font(bold=True)
		self.resize_column(worksheet, current_row, 6)

		ticker_row = current_row + 1
		
		for i in range(0, len(self.portfolio_analyzer.portfolio.equities)):
			current_row += 1
			current_equity = self.portfolio_analyzer.portfolio.equities[i]

			# ticker
			worksheet.cell(row=current_row, column=3).value = current_equity.ticker
			self.resize_column(worksheet, current_row, 3)

			# weight
			mvp_weight = self.portfolio_analyzer.mvp[time_interval][i]
			worksheet.cell(row=current_row, column=4).value = mvp_weight
			self.resize_column(worksheet, current_row, 4)

			# shares
			mvp_shares = (mvp_weight * self.portfolio_analyzer.portfolio.value) / current_equity.price
			worksheet.cell(row=current_row, column=5).value = mvp_shares
			self.resize_column(worksheet, current_row, 5)

			# value change
			new_value = mvp_shares * current_equity.price
			old_value = current_equity.shares * current_equity.price
			value_change = new_value - old_value
			worksheet.cell(row=current_row, column=6).value = value_change
			self.resize_column(worksheet, current_row, 6)
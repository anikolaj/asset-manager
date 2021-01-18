import math
import numpy as np

from scipy.stats import pearsonr

def compute_covariance_with_correlation_coefficient(x_data, y_data, x_stdev, y_stdev):
	x_len = len(x_data)
	y_len = len(y_data)

	if x_len != y_len:
		diff = abs(x_len - y_len)
		if x_len > y_len:
			x_data = x_data[diff : x_len]
		else:
			y_data = y_data[diff : y_len]
	
	rho, p_val = pearsonr(x_data, y_data)
	covariance = rho * x_stdev * y_stdev
	
	return covariance

def calculate_expected_value(X, p):
	p_t = np.transpose(p)
	expected_value = round(X @ p_t, 8)
	return expected_value

def calculate_variance(C, p):
	p_t = np.transpose(p)
	variance = p @ C @ p_t
	variance = round(variance.item(), 8)
	return variance

def solve_quadratic_formula(a, b, c):
	r = (b ** 2) - (4 * a * c)

	if r == -1:
		return None

	x1 = (-b + math.sqrt(r)) / (2 * a)
	x2 = (-b - math.sqrt(r)) / (2 * a)

	return x1, x2
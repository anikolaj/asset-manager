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
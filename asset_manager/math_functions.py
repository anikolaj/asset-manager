from scipy.stats import pearsonr

def compute_covariance_with_correlation_coefficient(x_data, y_data, x_stdev, y_stdev):
	rho, p_val = pearsonr(x_data, y_data)
	covariance = rho * x_stdev * y_stdev
	return covariance
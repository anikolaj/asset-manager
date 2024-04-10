import asset_manager.utilities.math_functions as mf


def test_compute_covariance_with_correlation_coefficient():
    x_data = [1, 2, 3]
    y_data = [1, 2, 3]
    x_stdev = 2
    y_stdev = 4

    result = mf.compute_covariance_with_correlation_coefficient(x_data, y_data, x_stdev, y_stdev)
    rounded_result = round(result, 3)
    assert rounded_result == 8.0

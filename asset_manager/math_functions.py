import math
import numpy as np
from scipy.stats import pearsonr
from typing import Optional


def compute_covariance_with_correlation_coefficient(
    x_data: list[float],
    y_data: list[float],
    x_stdev: float,
    y_stdev: float,
) -> np.float64:
    x_len = len(x_data)
    y_len = len(y_data)

    if x_len != y_len:
        diff = abs(x_len - y_len)
        if x_len > y_len:
            x_data = x_data[diff:x_len]
        else:
            y_data = y_data[diff:y_len]

    rho, p_val = pearsonr(x_data, y_data)
    covariance = rho * x_stdev * y_stdev

    return covariance


def calculate_expected_value(X: np.ndarray, p: np.ndarray) -> float:
    p_t = np.transpose(p)
    expected_value = round(X @ p_t, 8)
    return float(expected_value)


def calculate_variance(C: np.ndarray, p: np.ndarray) -> float:
    p_t = np.transpose(p)

    variance = p @ C @ p_t
    variance = round(variance.item(), 8)

    return variance


def solve_quadratic_formula(
    a: np.float64, b: np.float64, c: np.float64
) -> Optional[tuple[np.float64, np.float64]]:
    r = (b**2) - (4 * a * c)

    if r == -1:
        return None

    x1 = (-b + math.sqrt(r)) / (2 * a)
    x2 = (-b - math.sqrt(r)) / (2 * a)

    return x1, x2

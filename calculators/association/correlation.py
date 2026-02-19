
# ==========================================
# Correlation — Sample Size
# ==========================================

import math

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout
)


def calculate_correlation(
    alpha: float,
    power: float,
    r: float,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates required sample size for detecting correlation.

    Uses Fisher z-transformation.
    """

    if r <= -0.99 or r >= 0.99:
        raise ValueError("Correlation must be between -0.99 and 0.99.")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    z = 0.5 * math.log((1 + r) / (1 - r))

    n_raw = ((Z_alpha + Z_beta) ** 2) / (z ** 2) + 3

    n_ceiled = ceil_int(n_raw)
    n_final = adjust_for_dropout(n_ceiled, dropout_rate)

    return {
        "n_required": n_final,
        "n_before_dropout": n_ceiled,
        "formula": "Fisher z-transformation method",
        "assumptions": [
            "Bivariate normal distribution",
            "Testing H0: rho = 0",
            "Large-sample approximation"
        ]
    }

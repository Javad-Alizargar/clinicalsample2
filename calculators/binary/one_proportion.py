
# ==========================================
# One Proportion — Sample Size
# ==========================================

import math

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_proportion
)


def calculate_one_proportion(
    alpha: float,
    power: float,
    p0: float,
    p1: float,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for one-sample proportion test.

    Formula:
    n = ((Z_alpha * sqrt(p0(1-p0)) +
          Z_beta * sqrt(p1(1-p1)))^2) / (p1 - p0)^2
    """

    p0 = validate_proportion(p0)
    p1 = validate_proportion(p1)

    if p1 == p0:
        raise ValueError("p1 must differ from p0.")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    numerator = (
        Z_alpha * math.sqrt(p0 * (1 - p0)) +
        Z_beta * math.sqrt(p1 * (1 - p1))
    ) ** 2

    denominator = (p1 - p0) ** 2

    n_raw = numerator / denominator

    n_ceiled = ceil_int(n_raw)
    n_final = adjust_for_dropout(n_ceiled, dropout_rate)

    return {
        "n_required": n_final,
        "n_before_dropout": n_ceiled,
        "formula": "Normal approximation for one-sample proportion",
        "assumptions": [
            "Large sample normal approximation",
            "Binomial distribution",
            "Two-sided or one-sided test specified"
        ]
    }

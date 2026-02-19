
# ==========================================
# Linear Regression — Sample Size
# ==========================================

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_positive
)


def calculate_linear_regression(
    alpha: float,
    power: float,
    f2: float,
    n_predictors: int,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for multiple linear regression.

    f2 = Cohen's f²
    n_predictors = number of predictors tested
    """

    validate_positive(f2, "Cohen's f²")

    if n_predictors < 1:
        raise ValueError("Number of predictors must be at least 1.")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    n_raw = ((Z_alpha + Z_beta) ** 2) / f2 + n_predictors + 1

    n_ceiled = ceil_int(n_raw)
    n_final = adjust_for_dropout(n_ceiled, dropout_rate)

    return {
        "n_required": n_final,
        "n_before_dropout": n_ceiled,
        "formula": "n ≈ ((Z_alpha + Z_beta)^2 / f²) + predictors + 1",
        "assumptions": [
            "Multiple linear regression",
            "Effect size expressed as Cohen's f²",
            "Approximate planning formula"
        ]
    }

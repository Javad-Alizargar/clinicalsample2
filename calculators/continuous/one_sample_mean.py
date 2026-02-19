
# ==========================================
# One-Sample Mean — Sample Size Calculation
# ==========================================

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_positive
)


def calculate_one_sample_mean(
    alpha: float,
    power: float,
    sd: float,
    delta: float,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates required sample size for one-sample mean test.

    Formula:
    n = ((Z_alpha + Z_beta) * sd / delta)^2
    """

    validate_positive(sd, "Standard deviation")
    validate_positive(delta, "Mean difference")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    n_raw = ((Z_alpha + Z_beta) * sd / delta) ** 2
    n_ceiled = ceil_int(n_raw)
    n_final = adjust_for_dropout(n_ceiled, dropout_rate)

    return {
        "n_required": n_final,
        "n_before_dropout": n_ceiled,
        "formula": "n = ((Z_alpha + Z_beta) * sd / delta)^2",
        "assumptions": [
            "Outcome approximately normally distributed",
            "Known or estimated SD from literature or pilot",
            "Two-sided or one-sided test specified"
        ]
    }

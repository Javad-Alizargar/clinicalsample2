
# ==========================================
# Paired Mean — Sample Size
# ==========================================

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_positive
)


def calculate_paired_mean(
    alpha: float,
    power: float,
    sd_diff: float,
    delta: float,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates required sample size for paired mean comparison.

    sd_diff = standard deviation of within-subject differences

    Formula:
    n = ((Z_alpha + Z_beta) * sd_diff / delta)^2
    """

    validate_positive(sd_diff, "SD of differences")
    validate_positive(delta, "Mean difference")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    n_raw = ((Z_alpha + Z_beta) * sd_diff / delta) ** 2
    n_ceiled = ceil_int(n_raw)
    n_final = adjust_for_dropout(n_ceiled, dropout_rate)

    return {
        "n_required": n_final,
        "n_before_dropout": n_ceiled,
        "formula": "n = ((Z_alpha + Z_beta) * sd_diff / delta)^2",
        "assumptions": [
            "Paired or repeated measurements",
            "Differences approximately normally distributed",
            "SD is SD of differences (not raw SD)"
        ]
    }

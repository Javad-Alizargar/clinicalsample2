
# ==========================================
# Two Independent Means — Sample Size
# ==========================================

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_positive
)


def calculate_two_independent_means(
    alpha: float,
    power: float,
    sd: float,
    delta: float,
    allocation_ratio: float = 1.0,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for comparing two independent means.

    allocation_ratio = n2 / n1

    Formula:
    n1 = (1 + 1/r) * ((Z_alpha + Z_beta) * sd / delta)^2
    n2 = r * n1
    """

    validate_positive(sd, "Standard deviation")
    validate_positive(delta, "Mean difference")
    validate_positive(allocation_ratio, "Allocation ratio")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    r = allocation_ratio

    n1_raw = (1 + 1/r) * ((Z_alpha + Z_beta) * sd / delta) ** 2
    n2_raw = r * n1_raw

    n1 = ceil_int(n1_raw)
    n2 = ceil_int(n2_raw)

    n1_final = adjust_for_dropout(n1, dropout_rate)
    n2_final = adjust_for_dropout(n2, dropout_rate)

    return {
        "n_group1": n1_final,
        "n_group2": n2_final,
        "n_total": n1_final + n2_final,
        "n_before_dropout_group1": n1,
        "n_before_dropout_group2": n2,
        "formula": "n1 = (1 + 1/r) * ((Z_alpha + Z_beta) * sd / delta)^2",
        "assumptions": [
            "Independent groups",
            "Common SD (pooled estimate)",
            "Normal approximation",
            "Allocation ratio specified"
        ]
    }

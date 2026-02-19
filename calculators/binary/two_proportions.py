# ==========================================
# Two Proportions — Sample Size Calculation
# ==========================================

import math
from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_proportion,
    validate_positive
)

def calculate_two_proportions(
    alpha: float,
    power: float,
    p1: float,
    p2: float,
    allocation_ratio: float = 1.0,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for comparing two independent proportions.

    p1 = proportion in group 1
    p2 = proportion in group 2
    allocation_ratio = n2 / n1
    """

    # Validation
    p1 = validate_proportion(p1)
    p2 = validate_proportion(p2)
    validate_positive(allocation_ratio, "Allocation ratio")

    delta = abs(p1 - p2)

    if delta == 0:
        raise ValueError("Proportions must differ to compute sample size.")

    # Z values
    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    r = allocation_ratio

    # Pooled proportion under H0
    p_bar = (p1 + r * p2) / (1 + r)

    # Variance terms
    var_null = p_bar * (1 - p_bar) * (1 + 1/r)
    var_alt = (p1 * (1 - p1) + (p2 * (1 - p2)) / r)

    n1_raw = ((Z_alpha * math.sqrt(var_null) +
               Z_beta * math.sqrt(var_alt)) ** 2) / (delta ** 2)

    n1 = ceil_int(n1_raw)
    n2 = ceil_int(r * n1)

    n1_adj = adjust_for_dropout(n1, dropout_rate)
    n2_adj = adjust_for_dropout(n2, dropout_rate)

    return {
        "n_group1": n1_adj,
        "n_group2": n2_adj,
        "n_total": n1_adj + n2_adj,
        "n1_before_dropout": n1,
        "n2_before_dropout": n2,
        "formula": "Two-proportion Z-test (pooled variance approach)",
        "assumptions": [
            "Independent groups",
            "Binary outcome",
            "Normal approximation valid",
            "Adequate expected cell counts"
        ]
    }

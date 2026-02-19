
# ==========================================
# Survival (Log-Rank) — Sample Size
# ==========================================

import math

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_positive
)


def calculate_logrank(
    alpha: float,
    power: float,
    hazard_ratio: float,
    allocation_ratio: float = 1.0,
    event_fraction: float = 0.5,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for survival analysis using log-rank test.

    hazard_ratio = target HR
    allocation_ratio = n2 / n1
    event_fraction = expected proportion of participants with events
    """

    validate_positive(hazard_ratio, "Hazard ratio")
    validate_positive(allocation_ratio, "Allocation ratio")
    validate_positive(event_fraction, "Event fraction")

    if event_fraction >= 1:
        raise ValueError("Event fraction must be less than 1.")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)

    r = allocation_ratio
    p1 = 1 / (1 + r)
    p2 = r / (1 + r)

    # Required number of events
    D_raw = ((Z_alpha + Z_beta) ** 2) / (
        (math.log(hazard_ratio) ** 2) * p1 * p2
    )

    D = ceil_int(D_raw)

    # Convert events to total sample size
    N_raw = D / event_fraction
    N = ceil_int(N_raw)
    N_final = adjust_for_dropout(N, dropout_rate)

    n1 = ceil_int(N_final * p1)
    n2 = ceil_int(N_final * p2)

    return {
        "n_total": n1 + n2,
        "n_group1": n1,
        "n_group2": n2,
        "required_events": D,
        "n_before_dropout": N,
        "formula": "Freedman log-rank events-based formula",
        "assumptions": [
            "Proportional hazards assumption",
            "Log-rank test",
            "Event fraction estimated accurately"
        ]
    }

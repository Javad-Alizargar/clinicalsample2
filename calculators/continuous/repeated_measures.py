# calculators/continuous/repeated_measures.py

from utils.stat_utils import (
    z_alpha,
    z_beta,
    ceil_int,
    adjust_for_dropout,
    validate_positive,
    validate_proportion
)

def calculate_repeated_measures(
    alpha: float,
    power: float,
    sd: float,
    delta: float,
    m: int,
    rho: float,
    scenario: str,
    allocation_ratio: float = 1.0,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for repeated measures (longitudinal) designs.
    
    m = number of measurements per subject
    rho = correlation between repeated measurements
    scenario = "average" (Scenario A) or "interaction" (Scenario B)
    """
    validate_positive(sd, "Standard deviation")
    validate_positive(delta, "Mean difference")
    validate_positive(allocation_ratio, "Allocation ratio")
    
    if m < 2:
        raise ValueError("Multiple measurements requires at least 2 time points (m).")
    if rho <= -1 or rho >= 1:
        raise ValueError("Correlation (rho) must be strictly between -1 and 1.")

    Z_alpha = z_alpha(alpha, two_sided)
    Z_beta = z_beta(power)
    r = allocation_ratio

    # 1. Calculate standard (cross-sectional) N for group 1
    # n1_standard = (1 + 1/r) * ((Z_alpha + Z_beta) * sd / delta)^2
    n1_standard = (1 + 1/r) * ((Z_alpha + Z_beta) * sd / delta) ** 2

    # 2. Apply the Repeated Measures Adjustment Factor
    if scenario == "average":
        # Scenario A: Difference in overall average across time points
        adjustment = (1 + (m - 1) * rho) / m
        formula_used = "N_rep = N_std * (1 + (m-1)ρ) / m"
    else:
        # Scenario B: Difference in change over time (Interaction)
        adjustment = (1 - rho)
        formula_used = "N_rep = N_std * (1 - ρ)"

    n1_raw = n1_standard * adjustment
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
        "adjustment_factor": round(adjustment, 4),
        "formula": formula_used,
        "assumptions": [
            "Continuous outcome",
            "Compound symmetry (constant correlation ρ between all time points)",
            "Adjustment applied to standard independent means formula"
        ]
    }

# ==========================================
# Cohort / Risk Ratio — Sample Size
# ==========================================

from utils.stat_utils import validate_proportion, validate_positive
from calculators.binary.two_proportions import calculate_two_proportions


def calculate_cohort_rr(
    alpha: float,
    power: float,
    baseline_risk: float,
    risk_ratio: float,
    allocation_ratio: float = 1.0,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for cohort or RCT with binary outcome.

    baseline_risk = risk in control group (p0)
    risk_ratio = target RR
    """

    p0 = validate_proportion(baseline_risk)
    validate_positive(risk_ratio, "Risk ratio")
    validate_positive(allocation_ratio, "Allocation ratio")

    p1 = p0 * risk_ratio

    if p1 >= 1:
        raise ValueError("Risk ratio too large for given baseline risk.")

    result = calculate_two_proportions(
        alpha=alpha,
        power=power,
        p1=p1,
        p2=p0,
        allocation_ratio=allocation_ratio,
        two_sided=two_sided,
        dropout_rate=dropout_rate
    )

    result["formula"] = "Derived p1 = RR × p0 and applied two-proportion normal approximation"
    result["assumptions"].append("Cohort or randomized controlled design")

    return result

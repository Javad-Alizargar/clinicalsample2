
# ==========================================
# Case-Control (Odds Ratio) — Sample Size
# ==========================================

from utils.stat_utils import validate_proportion, validate_positive
from calculators.binary.two_proportions import calculate_two_proportions


def calculate_case_control_or(
    alpha: float,
    power: float,
    p0: float,
    odds_ratio: float,
    control_case_ratio: float = 1.0,
    two_sided: bool = True,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates sample size for unmatched case-control study.

    p0 = exposure prevalence among controls
    odds_ratio = target OR
    control_case_ratio = number of controls per case
    """

    p0 = validate_proportion(p0)
    validate_positive(odds_ratio, "Odds ratio")
    validate_positive(control_case_ratio, "Control-case ratio")

    # Derive exposure prevalence among cases
    p1 = (odds_ratio * p0) / (1 - p0 + odds_ratio * p0)

    result = calculate_two_proportions(
        alpha=alpha,
        power=power,
        p1=p1,
        p2=p0,
        allocation_ratio=control_case_ratio,
        two_sided=two_sided,
        dropout_rate=dropout_rate
    )

    result["formula"] = "Derived p1 from OR and applied two-proportion normal approximation"
    result["assumptions"].append("Unmatched case-control design")

    return result

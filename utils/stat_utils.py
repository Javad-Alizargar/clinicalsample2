
# ==========================================
# ClinSample AI — Statistical Utilities
# ==========================================

import math
from scipy.stats import norm


def z_alpha(alpha: float, two_sided: bool = True) -> float:
    """
    Returns Z critical value for given alpha.
    """
    if two_sided:
        return norm.ppf(1 - alpha/2)
    return norm.ppf(1 - alpha)


def z_beta(power: float) -> float:
    """
    Returns Z value corresponding to desired power (1 - beta).
    """
    return norm.ppf(power)


def ceil_int(x: float) -> int:
    """
    Always round up to next integer.
    """
    return int(math.ceil(x))


def adjust_for_dropout(n: int, dropout_rate: float) -> int:
    """
    Adjust sample size for expected dropout proportion.
    Example: dropout_rate = 0.10 for 10%.
    """
    if dropout_rate < 0:
        dropout_rate = 0
    if dropout_rate >= 0.95:
        raise ValueError("Dropout rate too high.")
    return ceil_int(n / (1 - dropout_rate))


def validate_proportion(p: float) -> float:
    """
    Ensures proportion is between 0 and 1.
    """
    if p <= 0 or p >= 1:
        raise ValueError("Proportion must be between 0 and 1 (exclusive).")
    return p


def validate_positive(value: float, name: str = "Value") -> float:
    """
    Ensures parameter is positive.
    """
    if value <= 0:
        raise ValueError(f"{name} must be positive.")
    return value

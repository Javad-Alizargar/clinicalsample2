
# ==========================================
# One-Way ANOVA — Sample Size
# ==========================================

from utils.stat_utils import adjust_for_dropout, ceil_int
from statsmodels.stats.power import FTestAnovaPower


def calculate_anova_oneway(
    alpha: float,
    power: float,
    effect_size_f: float,
    k_groups: int,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates required sample size for one-way ANOVA.

    effect_size_f = Cohen's f
    k_groups = number of groups

    Uses F-test power calculation.
    """

    if effect_size_f <= 0:
        raise ValueError("Effect size f must be positive.")

    if k_groups < 2:
        raise ValueError("Number of groups must be at least 2.")

    analysis = FTestAnovaPower()

    n_total_raw = analysis.solve_power(
        effect_size=effect_size_f,
        nobs=None,
        alpha=alpha,
        power=power,
        k_groups=k_groups
    )

    n_total = ceil_int(n_total_raw)
    n_total_final = adjust_for_dropout(n_total, dropout_rate)

    n_per_group = ceil_int(n_total_final / k_groups)

    return {
        "n_total": n_per_group * k_groups,
        "n_per_group": n_per_group,
        "n_before_dropout": n_total,
        "formula": "Solved using FTestAnovaPower with Cohen's f",
        "assumptions": [
            "One-way fixed effect ANOVA",
            "Balanced design assumed",
            "Effect size expressed as Cohen's f"
        ]
    }

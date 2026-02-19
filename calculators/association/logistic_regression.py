
# ==========================================
# Logistic Regression — Sample Size (EPV)
# ==========================================

from utils.stat_utils import (
    ceil_int,
    adjust_for_dropout,
    validate_positive,
    validate_proportion
)


def calculate_logistic_regression(
    event_rate: float,
    n_predictors: int,
    epv: int = 10,
    dropout_rate: float = 0.0
) -> dict:
    """
    Calculates minimum sample size for logistic regression
    using Events Per Variable (EPV) rule.

    event_rate = outcome prevalence
    n_predictors = number of predictors
    epv = events per variable (default 10)
    """

    event_rate = validate_proportion(event_rate)
    validate_positive(n_predictors, "Number of predictors")
    validate_positive(epv, "EPV")

    required_events = epv * n_predictors
    n_raw = required_events / event_rate

    n_ceiled = ceil_int(n_raw)
    n_final = adjust_for_dropout(n_ceiled, dropout_rate)

    return {
        "n_required": n_final,
        "required_events": required_events,
        "n_before_dropout": n_ceiled,
        "formula": "N = (EPV × predictors) / event_rate",
        "assumptions": [
            "Logistic regression planning rule",
            "EPV ensures model stability",
            "Not a hypothesis-testing power calculation"
        ]
    }

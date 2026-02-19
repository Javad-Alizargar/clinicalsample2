
# ==========================================
# Thesis / Manuscript Paragraph Templates
# ==========================================

def paragraph_one_sample_mean(alpha, power, sd, delta, two_sided, dropout_rate, n_required):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated for a one-sample mean test ({sided}) with α={alpha:.3g} and power={power:.3g}. "
        f"Assuming a standard deviation (SD) of {sd:g} and a clinically meaningful difference (Δ) of {delta:g}, "
        f"the required sample size was {n_required} participants after adjusting for an anticipated dropout rate of "
        f"{dropout_rate*100:.1f}%."
    )


def paragraph_two_independent_means(alpha, power, sd, delta, allocation_ratio, two_sided, dropout_rate, n1, n2):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated for a two-sample comparison of means ({sided}) with α={alpha:.3g} and power={power:.3g}. "
        f"Assuming a common SD of {sd:g} and an expected mean difference (Δ) of {delta:g}, "
        f"with an allocation ratio of {allocation_ratio:g} (group 2 / group 1), the required sample size was "
        f"{n1} in group 1 and {n2} in group 2 after adjusting for an anticipated dropout rate of {dropout_rate*100:.1f}%."
    )


def paragraph_paired_mean(alpha, power, sd_diff, delta, two_sided, dropout_rate, n_required):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated for a paired mean difference test ({sided}) with α={alpha:.3g} and power={power:.3g}. "
        f"Assuming the SD of within-subject differences (SDd) was {sd_diff:g} and the expected mean difference (Δ) was {delta:g}, "
        f"the required sample size was {n_required} paired observations after adjusting for an anticipated dropout rate of "
        f"{dropout_rate*100:.1f}%."
    )


def paragraph_anova(alpha, power, effect_size_f, k_groups, dropout_rate, n_total, n_per_group):
    return (
        f"Sample size was calculated for a one-way ANOVA with {k_groups} groups, using α={alpha:.3g} and power={power:.3g}. "
        f"Assuming an effect size of Cohen’s f={effect_size_f:g} and a balanced design, the required total sample size was "
        f"{n_total} participants ({n_per_group} per group) after adjusting for an anticipated dropout rate of {dropout_rate*100:.1f}%."
    )


def paragraph_one_proportion(alpha, power, p0, p1, two_sided, dropout_rate, n_required):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated for a one-sample proportion test ({sided}) with α={alpha:.3g} and power={power:.3g}. "
        f"Assuming a null proportion p0={p0:g} and an alternative proportion p1={p1:g}, the required sample size was "
        f"{n_required} participants after adjusting for an anticipated dropout/non-evaluable rate of {dropout_rate*100:.1f}%."
    )


def paragraph_two_proportions(alpha, power, p1, p2, allocation_ratio, two_sided, dropout_rate, n1, n2):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated for a two-sample comparison of proportions ({sided}) with α={alpha:.3g} and power={power:.3g}. "
        f"Assuming proportions of p1={p1:g} (group 1) and p2={p2:g} (group 2), with an allocation ratio of {allocation_ratio:g} "
        f"(group 2 / group 1), the required sample size was {n1} in group 1 and {n2} in group 2 after adjusting for an anticipated "
        f"dropout/non-evaluable rate of {dropout_rate*100:.1f}%."
    )


def paragraph_case_control_or(alpha, power, p0, odds_ratio, control_case_ratio, two_sided, dropout_rate, n_cases, n_controls):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated for an unmatched case–control study to detect an odds ratio (OR) of {odds_ratio:g}, "
        f"assuming an exposure prevalence among controls of p0={p0:g}. Using a {sided} test with α={alpha:.3g} and power={power:.3g}, "
        f"and a control-to-case ratio of {control_case_ratio:g}, the required sample size was {n_cases} cases and {n_controls} controls "
        f"after adjusting for an anticipated dropout/non-evaluable rate of {dropout_rate*100:.1f}%."
    )


def paragraph_cohort_rr(alpha, power, baseline_risk, risk_ratio, allocation_ratio, two_sided, dropout_rate, n1, n2):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated for a two-group comparison of risks ({sided}) with α={alpha:.3g} and power={power:.3g}. "
        f"Assuming a baseline risk of p0={baseline_risk:g} and a target risk ratio (RR) of {risk_ratio:g}, with an allocation ratio "
        f"of {allocation_ratio:g} (group 2 / group 1), the required sample size was {n1} in group 1 and {n2} in group 2 after adjusting "
        f"for an anticipated dropout/non-evaluable rate of {dropout_rate*100:.1f}%."
    )


def paragraph_correlation(alpha, power, r, two_sided, dropout_rate, n_required):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated to detect a correlation of r={r:g} using Fisher’s z transformation with a {sided} test, "
        f"α={alpha:.3g}, and power={power:.3g}. The required sample size was {n_required} participants after adjusting for an anticipated "
        f"dropout rate of {dropout_rate*100:.1f}%."
    )


def paragraph_linear_regression(alpha, power, f2, n_predictors, two_sided, dropout_rate, n_required):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size for multiple linear regression was planned using an approximate effect size approach (Cohen’s f²={f2:g}) "
        f"with a {sided} α={alpha:.3g} and power={power:.3g}. Assuming {n_predictors} predictors in the model, the required sample size "
        f"was {n_required} participants after adjusting for an anticipated dropout rate of {dropout_rate*100:.1f}%."
    )


def paragraph_logistic_regression_epv(event_rate, n_predictors, epv, dropout_rate, n_required, required_events):
    return (
        f"Sample size for logistic regression was planned using an events-per-variable (EPV) approach. "
        f"Assuming an event rate of {event_rate:g} and {n_predictors} predictors, with EPV={epv}, at least {required_events} outcome events "
        f"and a total sample size of {n_required} participants were required after adjusting for an anticipated dropout rate of "
        f"{dropout_rate*100:.1f}%. "
        f"(Note: EPV is a model-stability planning rule rather than a hypothesis-testing power calculation.)"
    )


def paragraph_logrank(alpha, power, hazard_ratio, allocation_ratio, event_fraction, two_sided, dropout_rate, n1, n2, n_total, required_events):
    sided = "two-sided" if two_sided else "one-sided"
    return (
        f"Sample size was calculated for a log-rank test ({sided}) with α={alpha:.3g} and power={power:.3g}. "
        f"Assuming a hazard ratio (HR) of {hazard_ratio:g} and an allocation ratio of {allocation_ratio:g} (group 2 / group 1), "
        f"the required number of events was {required_events}. Given an expected event fraction of {event_fraction:g} during follow-up, "
        f"the required total sample size was {n_total} participants ({n1} in group 1 and {n2} in group 2) after adjusting for an anticipated "
        f"dropout rate of {dropout_rate*100:.1f}%."
    )

# ==========================================
# Cohort (Risk Ratio) — Modular Advanced Version
# Two-group risk comparison using baseline risk p0 + target RR
# Includes helpers to derive RR from risks, events/total, and CI
# ==========================================

import streamlit as st
import math
import scipy.stats as stats

from calculators.binary.cohort_rr import calculate_cohort_rr
from templates.paragraph_templates import paragraph_cohort_rr

from app.components.pubmed_section import render_pubmed_section


def _rr_from_risks(p1: float, p0: float):
    if p0 <= 0 or p0 >= 1 or p1 <= 0 or p1 >= 1:
        return None
    return p1 / p0


def _risk_from_events(events: int, total: int):
    if total <= 0:
        return None
    if events < 0 or events > total:
        return None
    return events / total


def _se_log_rr_from_ci(rr: float, ci_low: float, ci_high: float):
    if rr <= 0 or ci_low <= 0 or ci_high <= 0 or ci_low >= ci_high:
        return None
    z = stats.norm.ppf(0.975)
    return (math.log(ci_high) - math.log(ci_low)) / (2 * z)


def _pick_keys_cohort(result: dict) -> dict:
    """
    Normalize calculator outputs across possible naming conventions.
    We normalize to: n1, n2, n_total.
    (Group 1 = baseline/control; Group 2 = exposed/intervention)
    """
    candidates_g1 = ["n_group1", "n1", "group1", "control", "n_control"]
    candidates_g2 = ["n_group2", "n2", "group2", "exposed", "n_exposed"]
    candidates_total = ["n_total", "total", "N", "n"]

    n1 = None
    n2 = None
    n_total = None

    for k in candidates_g1:
        if k in result:
            n1 = result[k]
            break
    for k in candidates_g2:
        if k in result:
            n2 = result[k]
            break
    for k in candidates_total:
        if k in result:
            n_total = result[k]
            break

    if n_total is None and (n1 is not None) and (n2 is not None):
        try:
            n_total = int(n1) + int(n2)
        except Exception:
            n_total = None

    return {"n1": n1, "n2": n2, "n_total": n_total}


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("Cohort (Risk Ratio) — Sample Size Planning")

    # ==========================================================
    # Explanation
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Used when comparing **risks (cumulative incidence)** between **two independent groups**.

Examples:
- Exposed vs unexposed (cohort)
- Intervention vs usual care (risk endpoint)

Planning inputs:
- **p0**: baseline risk in Group 1 (control/unexposed)
- **RR**: target risk ratio to detect
- **Allocation ratio (r = n2/n1)**

Common abstract sources:
- Event rates in each group (events/total)
- Reported RR (with CI)
        """)

    # ==========================================================
    # Key relationships
    # ==========================================================
    with st.expander("📐 Key Relationship", expanded=False):
        st.latex(r"RR = \frac{p_2}{p_1}")
        st.caption("Here: Group 1 baseline risk = p0; Group 2 risk = RR × p0 (capped < 1).")

    # ==========================================================
    # RR extraction helpers
    # ==========================================================
    st.subheader("🧠 Derive RR from common abstract statistics")

    tab_rr_direct, tab_rates, tab_events, tab_ci = st.tabs([
        "A) Enter RR directly",
        "B) RR from two risks",
        "C) RR from events/total",
        "D) RR from 95% CI (log-scale SE)"
    ])

    with tab_rr_direct:
        st.number_input("Target RR (planning)", min_value=0.01, value=1.5, step=0.05, key="rr_direct")
        st.caption("If literature reports an adjusted RR close to your target, use it here.")

    with tab_rates:
        st.markdown("If abstract reports two risks (proportions), compute RR.")
        p0_tmp = st.number_input("Risk in Group 1 (p0)", min_value=0.0001, max_value=0.9999, value=0.20, step=0.01, key="rr_p0_tmp")
        p2_tmp = st.number_input("Risk in Group 2 (p2)", min_value=0.0001, max_value=0.9999, value=0.30, step=0.01, key="rr_p2_tmp")

        if st.button("Compute RR from risks", key="rr_from_risks_btn"):
            rr = _rr_from_risks(p2_tmp, p0_tmp)
            if rr is None:
                st.error("Invalid risks.")
            else:
                st.success(f"RR = {rr:.4f}")

    with tab_events:
        st.markdown("If abstract reports events and totals for each group, compute risks then RR.")
        col1, col2 = st.columns(2)
        with col1:
            e1 = st.number_input("Events Group 1", min_value=0, value=20, step=1, key="rr_e1")
            n1 = st.number_input("Total Group 1", min_value=1, value=100, step=1, key="rr_n1")
        with col2:
            e2 = st.number_input("Events Group 2", min_value=0, value=30, step=1, key="rr_e2")
            n2 = st.number_input("Total Group 2", min_value=1, value=100, step=1, key="rr_n2")

        if st.button("Compute risks + RR", key="rr_from_events_btn"):
            p1 = _risk_from_events(int(e1), int(n1))
            p2 = _risk_from_events(int(e2), int(n2))
            if p1 is None or p2 is None or p1 == 0:
                st.error("Invalid events/total (and Group 1 risk must be > 0).")
            else:
                rr = p2 / p1
                st.write(f"p0 (Group 1) = {p1:.4f}")
                st.write(f"p2 (Group 2) = {p2:.4f}")
                st.success(f"RR = {rr:.4f}")

    with tab_ci:
        st.markdown("If abstract reports RR with 95% CI, estimate SE[log(RR)].")
        rr_point = st.number_input("RR (point estimate)", min_value=0.01, value=1.5, step=0.05, key="rr_point")
        ci_low = st.number_input("CI lower", min_value=0.0001, value=1.05, step=0.05, key="rr_ci_low")
        ci_high = st.number_input("CI upper", min_value=0.0001, value=2.10, step=0.05, key="rr_ci_high")

        if st.button("Estimate log(RR) SE", key="rr_ci_btn"):
            se = _se_log_rr_from_ci(rr_point, ci_low, ci_high)
            if se is None:
                st.error("Invalid RR/CI values.")
            else:
                st.success(f"SE[log(RR)] ≈ {se:.4f}")
                st.caption("Mostly for QA/reporting; planning uses p0 + RR + allocation ratio.")

    # ==========================================================
    # PubMed helper
    # ==========================================================
    render_pubmed_section(
        study_type="Cohort (Risk Ratio)",
        default_outcome="incidence",
        default_population="cohort",
        default_extra="risk ratio OR relative risk OR incidence",
        key_prefix="cohort_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final planning inputs
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    baseline_risk = st.number_input(
        "Baseline risk in Group 1 (p0)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        step=0.01,
        key="cohort_p0"
    )

    risk_ratio = st.number_input(
        "Target Risk Ratio (RR)",
        min_value=0.01,
        value=1.5,
        step=0.05,
        key="cohort_rr"
    )

    allocation_ratio = st.number_input(
        "Allocation ratio (n2/n1)",
        min_value=0.1,
        value=1.0,
        step=0.1,
        key="cohort_ratio"
    )

    if st.button("Calculate Sample Size", key="cohort_calc_btn"):
        if dropout_rate >= 0.95:
            st.error("Dropout rate too high. Please use < 0.95.")
            st.stop()

        try:
            result = calculate_cohort_rr(
                alpha=alpha,
                power=power,
                baseline_risk=baseline_risk,
                risk_ratio=risk_ratio,
                allocation_ratio=allocation_ratio,
                two_sided=two_sided,
                dropout_rate=dropout_rate
            )
        except TypeError:
            # fallback if implementation uses different param names / positional args
            result = calculate_cohort_rr(alpha, power, baseline_risk, risk_ratio, allocation_ratio, two_sided, dropout_rate)

        norm = _pick_keys_cohort(result)
        if norm["n1"] is None or norm["n2"] is None:
            st.error(
                "Calculator returned unexpected keys.\n\n"
                f"Returned keys: {sorted(list(result.keys()))}\n\n"
                "Expected one of:\n"
                "- group1: n_group1 / n1\n"
                "- group2: n_group2 / n2\n"
                "- total: n_total (optional)"
            )
            st.stop()

        Z_alpha = stats.norm.ppf(1 - alpha / 2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {Z_alpha:.4f}")
        st.write(f"Zβ = {Z_beta:.4f}")

        st.success(f"Group 1 required: {int(norm['n1'])}")
        st.success(f"Group 2 required: {int(norm['n2'])}")
        if norm["n_total"] is not None:
            st.write("Total sample size:", int(norm["n_total"]))

        paragraph = paragraph_cohort_rr(
            alpha=alpha,
            power=power,
            baseline_risk=baseline_risk,
            risk_ratio=risk_ratio,
            allocation_ratio=allocation_ratio,
            two_sided=two_sided,
            dropout_rate=dropout_rate,
            n1=int(norm["n1"]),
            n2=int(norm["n2"])
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)
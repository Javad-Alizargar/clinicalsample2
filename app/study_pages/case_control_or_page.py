# ==========================================
# Case-Control (Odds Ratio) — Modular Advanced Version
# Unmatched case–control planning using exposure prevalence in controls (p0) + target OR
# Robust to different calculator return-key conventions
# ==========================================

import streamlit as st
import math
import scipy.stats as stats

from calculators.binary.case_control_or import calculate_case_control_or
from templates.paragraph_templates import paragraph_case_control_or

from app.components.pubmed_section import render_pubmed_section


def _or_from_2x2(a, b, c, d):
    """
    OR = (a*d)/(b*c) for:
        Exposed  Unexposed
    Case   a        b
    Ctrl   c        d
    """
    if min(a, b, c, d) <= 0:
        return None
    return (a * d) / (b * c)


def _rr_to_or(rr, p0):
    """
    Convert RR to OR given baseline risk p0:
    OR = RR*(1-p0)/(1 - RR*p0)
    """
    if rr <= 0 or p0 <= 0 or p0 >= 1:
        return None
    denom = (1 - rr * p0)
    if denom <= 0:
        return None
    return rr * (1 - p0) / denom


def _pick_keys_case_control(result: dict) -> dict:
    """
    Different implementations may return different key names.
    We normalize to: n_cases, n_controls, n_total.
    """
    # Possible conventions we support
    candidates_cases = ["n_cases", "cases", "n_case", "n1", "n_group1"]
    candidates_controls = ["n_controls", "controls", "n_control", "n2", "n_group2"]
    candidates_total = ["n_total", "total", "N", "n"]

    n_cases = None
    n_controls = None
    n_total = None

    for k in candidates_cases:
        if k in result:
            n_cases = result[k]
            break

    for k in candidates_controls:
        if k in result:
            n_controls = result[k]
            break

    for k in candidates_total:
        if k in result:
            n_total = result[k]
            break

    # If total missing, try compute
    if n_total is None and (n_cases is not None) and (n_controls is not None):
        try:
            n_total = int(n_cases) + int(n_controls)
        except Exception:
            n_total = None

    return {"n_cases": n_cases, "n_controls": n_controls, "n_total": n_total}


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("Case-Control (Odds Ratio) — Sample Size Planning")

    # ==========================================================
    # Explanation
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
A **case–control study** starts with outcome status (case vs control) and compares **exposure prevalence** between groups.

You plan sample size using:
- **p0**: exposure prevalence among controls
- **Target OR**: odds ratio you want to detect
- **Control:case ratio (m)**

Typical sources from abstracts:
- Exposure prevalence in controls (or overall)
- Reported OR (with CI) from logistic regression
- 2×2 table counts (sometimes in abstract or results)
        """)

    # ==========================================================
    # Core formulas
    # ==========================================================
    with st.expander("📐 Core Formulas (for understanding)", expanded=False):
        st.markdown("### Convert OR + p0 to exposure prevalence among cases (p1)")
        st.latex(r"p_1 = \frac{OR \cdot p_0}{1 - p_0 + OR \cdot p_0}")
        st.caption("The calculator uses this internally and then applies a Z-test approximation + dropout adjustment.")

    # ==========================================================
    # OR extraction helpers
    # ==========================================================
    st.subheader("🧠 Derive OR from common abstract statistics")

    tab_or_direct, tab_2x2, tab_ci, tab_rr = st.tabs([
        "A) Enter OR directly",
        "B) OR from 2×2 counts",
        "C) OR from 95% CI (log-scale SE)",
        "D) Approx OR from RR"
    ])

    with tab_or_direct:
        st.number_input("Target OR (planning)", min_value=0.01, value=1.8, step=0.05, key="cc_or_direct")
        st.caption("If literature reports an adjusted OR close to your target effect, use it here.")

    with tab_2x2:
        st.markdown("If you can reconstruct a 2×2 table, compute OR.")
        col1, col2 = st.columns(2)
        with col1:
            a = st.number_input("Cases exposed (a)", min_value=0, value=30, step=1, key="cc_a")
            b = st.number_input("Cases unexposed (b)", min_value=0, value=70, step=1, key="cc_b")
        with col2:
            c = st.number_input("Controls exposed (c)", min_value=0, value=20, step=1, key="cc_c")
            d = st.number_input("Controls unexposed (d)", min_value=0, value=80, step=1, key="cc_d")

        if st.button("Compute OR from 2×2", key="cc_or_2x2_btn"):
            or_2x2 = _or_from_2x2(a, b, c, d)
            if or_2x2 is None:
                st.error("Need all four cells > 0 to compute OR (no zeros).")
            else:
                st.success(f"OR = {or_2x2:.4f}")

    with tab_ci:
        st.markdown("If abstract reports OR with 95% CI, estimate SE[log(OR)].")
        or_point = st.number_input("OR (point estimate)", min_value=0.01, value=1.8, step=0.05, key="cc_or_point")
        ci_low = st.number_input("CI lower", min_value=0.0001, value=1.1, step=0.05, key="cc_or_ci_low")
        ci_high = st.number_input("CI upper", min_value=0.0001, value=2.9, step=0.05, key="cc_or_ci_high")

        if st.button("Estimate log(OR) SE", key="cc_or_ci_btn"):
            if ci_low <= 0 or ci_high <= 0 or ci_low >= ci_high:
                st.error("CI bounds must be positive and CI lower < CI upper.")
            else:
                z = stats.norm.ppf(0.975)
                se_log_or = (math.log(ci_high) - math.log(ci_low)) / (2 * z)
                st.success(f"SE[log(OR)] ≈ {se_log_or:.4f}")
                st.caption("This is mainly for QA/reporting; planning uses OR + p0 + ratio.")

        st.caption(f"Current OR = {or_point:.4f}")

    with tab_rr:
        st.markdown("Convert RR to OR approximately using baseline risk p0.")
        rr = st.number_input("RR", min_value=0.01, value=1.8, step=0.05, key="cc_rr")
        p0_for_conv = st.number_input("Baseline risk p0 (0–1)", min_value=0.0001, max_value=0.9999, value=0.20, step=0.01, key="cc_p0_conv")

        if st.button("Convert RR → OR", key="cc_rr_to_or_btn"):
            or_from_rr = _rr_to_or(rr, p0_for_conv)
            if or_from_rr is None:
                st.error("Conversion failed (check RR and p0).")
            else:
                st.success(f"Approx OR ≈ {or_from_rr:.4f}")

    # ==========================================================
    # PubMed helper
    # ==========================================================
    render_pubmed_section(
        study_type="Case-Control (Odds Ratio)",
        default_outcome="risk factor",
        default_population="case control",
        default_extra="odds ratio OR logistic regression OR prevalence controls",
        key_prefix="cc_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final planning inputs
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    p0 = st.number_input(
        "Exposure prevalence among controls (p0)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        step=0.01,
        key="cc_p0"
    )

    odds_ratio = st.number_input(
        "Target Odds Ratio (OR)",
        min_value=0.01,
        value=1.8,
        step=0.05,
        key="cc_or"
    )

    control_case_ratio = st.number_input(
        "Control-to-case ratio (m = controls/cases)",
        min_value=0.1,
        value=1.0,
        step=0.1,
        key="cc_ratio"
    )

    if st.button("Calculate Sample Size", key="cc_calc_btn"):
        if dropout_rate >= 0.95:
            st.error("Dropout rate too high. Please use < 0.95.")
            st.stop()

        try:
            result = calculate_case_control_or(
                alpha=alpha,
                power=power,
                p0=p0,
                odds_ratio=odds_ratio,
                control_case_ratio=control_case_ratio,
                two_sided=two_sided,
                dropout_rate=dropout_rate
            )
        except TypeError:
            # Fallback: some implementations may have positional or different param names.
            result = calculate_case_control_or(alpha, power, p0, odds_ratio, control_case_ratio, two_sided, dropout_rate)

        norm = _pick_keys_case_control(result)

        if norm["n_cases"] is None or norm["n_controls"] is None:
            st.error(
                "Calculator returned unexpected keys.\n\n"
                f"Returned keys: {sorted(list(result.keys()))}\n\n"
                "Expected one of:\n"
                "- cases: n_cases / cases / n1 / n_group1\n"
                "- controls: n_controls / controls / n2 / n_group2\n"
                "- total: n_total (optional)"
            )
            st.stop()

        Z_alpha = stats.norm.ppf(1 - alpha / 2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {Z_alpha:.4f}")
        st.write(f"Zβ = {Z_beta:.4f}")

        st.success(f"Cases required: {int(norm['n_cases'])}")
        st.success(f"Controls required: {int(norm['n_controls'])}")
        if norm["n_total"] is not None:
            st.write("Total sample size:", int(norm["n_total"]))

        paragraph = paragraph_case_control_or(
            alpha=alpha,
            power=power,
            p0=p0,
            odds_ratio=odds_ratio,
            control_case_ratio=control_case_ratio,
            two_sided=two_sided,
            dropout_rate=dropout_rate,
            n_cases=int(norm["n_cases"]),
            n_controls=int(norm["n_controls"])
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

# ==========================================
# Correlation — Modular Advanced Version
# Fisher z-based sample size planning
# Includes helpers to derive r from R^2 and from CI (approx)
# ==========================================

import streamlit as st
import math
import scipy.stats as stats

from templates.paragraph_templates import paragraph_correlation
from app.components.pubmed_section import render_pubmed_section


def _adjust_for_dropout(n: int, dropout_rate: float) -> int:
    if dropout_rate < 0:
        dropout_rate = 0.0
    if dropout_rate >= 0.95:
        raise ValueError("Dropout rate too high.")
    return int(math.ceil(n / (1.0 - dropout_rate)))


def _fisher_z(r: float) -> float:
    # clip to avoid infinite atanh
    r = max(min(r, 0.999999), -0.999999)
    return 0.5 * math.log((1 + r) / (1 - r))


def _n_for_correlation(alpha: float, power: float, r: float, two_sided: bool) -> int:
    """
    Fisher z approach:
      z_r = atanh(r)
      SE(z) = 1/sqrt(n-3)
      For H0: rho=0, test uses z_r / SE ~ Normal
      n = ( (Z_alpha + Z_beta) / z_r )^2 + 3
    """
    if abs(r) <= 0:
        raise ValueError("r must be non-zero.")
    if abs(r) >= 1:
        raise ValueError("r must be between -1 and 1.")

    Z_alpha = stats.norm.ppf(1 - alpha / 2) if two_sided else stats.norm.ppf(1 - alpha)
    Z_beta = stats.norm.ppf(power)

    z_r = abs(_fisher_z(r))
    n_raw = ((Z_alpha + Z_beta) / z_r) ** 2 + 3
    return int(math.ceil(n_raw))


def _r_from_r2(r2: float, sign: int = 1) -> float:
    r2 = float(r2)
    if r2 < 0 or r2 >= 1:
        return None
    r = math.sqrt(r2)
    return r if sign >= 0 else -r


def _se_z_from_ci(r_low: float, r_high: float) -> float:
    """
    Approximate SE in Fisher z scale from CI for r:
      z_low = atanh(r_low), z_high = atanh(r_high)
      SE ≈ (z_high - z_low)/(2*1.96)
    """
    if r_low <= -1 or r_low >= 1 or r_high <= -1 or r_high >= 1 or r_low >= r_high:
        return None
    z_low = _fisher_z(r_low)
    z_high = _fisher_z(r_high)
    return (z_high - z_low) / (2 * stats.norm.ppf(0.975))


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("Correlation — Sample Size Planning")

    # ==========================================================
    # Explanation
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Use when testing whether the correlation between two continuous variables differs from zero.

Examples:
- Biomarker level vs disease severity score
- Imaging metric vs cognitive score
- Dose vs response (continuous)

Key planning input:
- **Target correlation (r)** you consider meaningful (from literature/pilot)

Notes:
- Smaller |r| requires larger N.
- This calculator uses **Fisher’s z transformation**.
        """)

    # ==========================================================
    # Formula
    # ==========================================================
    with st.expander("📐 Mathematical Basis (Fisher z)", expanded=False):
        st.latex(r"z = \tanh^{-1}(r) = \frac{1}{2}\ln\left(\frac{1+r}{1-r}\right)")
        st.latex(r"SE(z) = \frac{1}{\sqrt{n-3}}")
        st.latex(r"n = \left(\frac{Z_{\alpha}+Z_{\beta}}{|z|}\right)^2 + 3")
        st.caption("Uses Zα = Φ⁻¹(1−α/2) for two-sided; Zα = Φ⁻¹(1−α) for one-sided.")

    # ==========================================================
    # r extraction helpers
    # ==========================================================
    st.subheader("🧠 Derive target r from common abstract statistics")

    tab_r, tab_r2, tab_ci = st.tabs([
        "A) Enter r directly",
        "B) Convert from R²",
        "C) CI helper (optional QA)"
    ])

    with tab_r:
        r_direct = st.number_input("Target correlation r", min_value=-0.99, max_value=0.99, value=0.30, step=0.01, key="corr_r_direct")
        st.caption("If the abstract reports r or Spearman rho (ρ), you can use it as a planning value (be explicit in Methods).")

    with tab_r2:
        st.markdown("If an abstract reports **R²** (e.g., from simple regression), convert to r.")
        r2 = st.number_input("R² (0–0.99)", min_value=0.0, max_value=0.99, value=0.09, step=0.01, key="corr_r2")
        sign = st.selectbox("Direction (sign of r)", ["Positive", "Negative"], index=0, key="corr_sign")
        if st.button("Convert R² → r", key="corr_r2_btn"):
            r = _r_from_r2(r2, sign=1 if sign == "Positive" else -1)
            if r is None:
                st.error("Invalid R².")
            else:
                st.success(f"r = {r:.4f}")

    with tab_ci:
        st.markdown("If an abstract reports r with 95% CI, estimate SE in z-scale (QA only).")
        r_low = st.number_input("r CI lower", min_value=-0.99, max_value=0.99, value=0.10, step=0.01, key="corr_ci_low")
        r_high = st.number_input("r CI upper", min_value=-0.99, max_value=0.99, value=0.50, step=0.01, key="corr_ci_high")
        if st.button("Estimate SE(z) from CI", key="corr_ci_btn"):
            se = _se_z_from_ci(r_low, r_high)
            if se is None:
                st.error("Invalid CI values.")
            else:
                st.success(f"SE(z) ≈ {se:.4f}")
                st.caption("For reporting/validation; planning uses target r.")

    # ==========================================================
    # PubMed helper
    # ==========================================================
    render_pubmed_section(
        study_type="Correlation",
        default_outcome="correlation coefficient",
        default_population="cohort",
        default_extra="correlation r OR Pearson OR Spearman",
        key_prefix="corr_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final calculation
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    r_plan = st.number_input(
        "Target correlation r (planning)",
        min_value=-0.99,
        max_value=0.99,
        value=0.30,
        step=0.01,
        key="corr_r_plan"
    )

    if st.button("Calculate Sample Size", key="corr_calc_btn"):
        if abs(r_plan) < 1e-12:
            st.error("Target r must be non-zero.")
            st.stop()

        n0 = _n_for_correlation(alpha=alpha, power=power, r=r_plan, two_sided=two_sided)
        n_final = _adjust_for_dropout(n0, dropout_rate)

        Z_alpha = stats.norm.ppf(1 - alpha / 2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {Z_alpha:.4f}")
        st.write(f"Zβ = {Z_beta:.4f}")
        st.write(f"Fisher z = {abs(_fisher_z(r_plan)):.4f}")

        st.success(f"Required sample size (after dropout): {n_final}")
        st.write("Before dropout adjustment:", n0)

        paragraph = paragraph_correlation(
            alpha=alpha,
            power=power,
            r=r_plan,
            two_sided=two_sided,
            dropout_rate=dropout_rate,
            n_required=n_final
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)
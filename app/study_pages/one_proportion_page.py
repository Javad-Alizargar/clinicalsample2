# ==========================================
# One Proportion — Modular Version
# ==========================================

import streamlit as st
import scipy.stats as stats
import math

from calculators.binary.one_proportion import calculate_one_proportion
from templates.paragraph_templates import paragraph_one_proportion

from app.components.pubmed_section import render_pubmed_section


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):

    st.header("One Proportion — Sample Size Planning")

    # ==========================================================
    # Study Explanation
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Used when estimating a single population proportion.

Examples:
• Prevalence of diabetes  
• Vaccine response rate  
• Complication rate  

Required:
• Expected proportion (p)
• Target / reference proportion (p₀) if hypothesis testing
        """)

    # ==========================================================
    # Formula
    # ==========================================================
    with st.expander("📐 Mathematical Formula", expanded=True):

        st.latex(r"""
        n =
        \frac{
        (Z_{\alpha} \sqrt{2p(1-p)} + Z_{\beta} \sqrt{p_1(1-p_1) + p_0(1-p_0)})^2
        }
        {(p_1 - p_0)^2}
        """)

        st.caption("Exact implementation depends on your calculator logic.")

    # ==========================================================
    # Extract Proportion Helpers
    # ==========================================================

    st.subheader("🧠 Derive Proportion from Common Abstract Formats")

    tab_direct, tab_counts, tab_ci = st.tabs([
        "A) Enter proportion directly",
        "B) From counts (events / total)",
        "C) From 95% CI"
    ])

    with tab_direct:
        p_direct = st.number_input(
            "Proportion (0–1)",
            min_value=0.0001,
            max_value=0.9999,
            value=0.30,
            step=0.01,
            key="oneprop_p_direct"
        )

    with tab_counts:
        events = st.number_input("Number of events", min_value=0, value=30, key="oneprop_events")
        total = st.number_input("Total sample size", min_value=1, value=100, key="oneprop_total")

        if st.button("Compute proportion", key="oneprop_compute_counts"):
            p_calc = events / total
            st.success(f"Proportion p = {round(p_calc,4)}")

    with tab_ci:
        lower = st.number_input("CI lower", min_value=0.0, value=0.25, key="oneprop_ci_lower")
        upper = st.number_input("CI upper", min_value=0.0, value=0.35, key="oneprop_ci_upper")

        if st.button("Estimate p from CI midpoint", key="oneprop_compute_ci"):
            p_mid = (lower + upper) / 2
            st.success(f"Estimated p ≈ {round(p_mid,4)}")

    # ==========================================================
    # PubMed Helper
    # ==========================================================

    render_pubmed_section(
        study_type="One Proportion",
        default_outcome="prevalence",
        default_population="cross sectional study",
        default_extra="proportion OR prevalence OR incidence",
        key_prefix="oneprop_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final Planning
    # ==========================================================

    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    p1 = st.number_input(
        "Expected proportion (p₁)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.30,
        key="oneprop_final_p1"
    )

    p0 = st.number_input(
        "Reference / null proportion (p₀)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        key="oneprop_final_p0"
    )

    if st.button("Calculate Sample Size", key="oneprop_calc_button"):

        if dropout_rate >= 0.95:
            st.error("Dropout rate too high.")
            st.stop()

        result = calculate_one_proportion(
            alpha,
            power,
            p1,
            p0,
            two_sided,
            dropout_rate
        )

        Z_alpha = stats.norm.ppf(1 - alpha/2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")

        st.success(f"Required Sample Size: {result['n_required']}")
        st.write("Before dropout adjustment:", result["n_before_dropout"])

        paragraph = paragraph_one_proportion(
            alpha,
            power,
            p1,
            p0,
            two_sided,
            dropout_rate,
            result["n_required"]
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

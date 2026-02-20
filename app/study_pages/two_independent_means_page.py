
# ==========================================
# Two Independent Means — Modular Version
# ==========================================

import streamlit as st
import scipy.stats as stats

from calculators.continuous.two_independent_means import calculate_two_independent_means
from templates.paragraph_templates import paragraph_two_independent_means

from app.components.stat_extraction import render_sd_extraction_section
from app.components.pubmed_section import render_pubmed_section


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):

    st.header("Two Independent Means — Sample Size Planning")

    # ==========================================================
    # Concept
    # ==========================================================

    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Used when comparing mean of two independent groups.

Examples:
• Treatment vs Control
• Male vs Female
• Drug A vs Drug B

Inputs required:
• SD (assumed equal or pooled)
• Mean difference (Δ)
• Allocation ratio (n1/n2)
        """)

    # ==========================================================
    # Formula
    # ==========================================================

    with st.expander("📐 Mathematical Formula", expanded=True):

        st.latex(r"""
        n = 2 \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD}{\Delta} \right)^2
        """)

    # ==========================================================
    # SD Extraction Component
    # ==========================================================

    render_sd_extraction_section(prefix="two_ind")

    # ==========================================================
    # Δ Helper
    # ==========================================================

    with st.expander("📊 Compute Mean Difference (Δ)", expanded=False):

        mean1 = st.number_input("Group 1 Mean", value=120.0, key="two_mean1")
        mean2 = st.number_input("Group 2 Mean", value=110.0, key="two_mean2")

        if st.button("Compute Δ", key="two_delta_button"):
            delta_calc = abs(mean1 - mean2)
            st.success(f"Δ = {round(delta_calc,4)}")

    # ==========================================================
    # PubMed Helper
    # ==========================================================

    render_pubmed_section(
        study_type="Two Independent Means",
        default_outcome="LDL cholesterol",
        default_population="randomized trial",
        default_extra="standard deviation OR mean difference",
        key_prefix="two_ind_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final Calculation
    # ==========================================================

    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    sd = st.number_input(
        "Standard Deviation (pooled)",
        min_value=0.0001,
        value=15.0,
        key="two_final_sd"
    )

    delta = st.number_input(
        "Mean difference (Δ)",
        min_value=0.0001,
        value=10.0,
        key="two_final_delta"
    )

    allocation_ratio = st.number_input(
        "Allocation ratio (n2/n1)",
        min_value=0.1,
        value=1.0,
        key="two_ratio"
    )

    if st.button("Calculate Sample Size", key="two_calc_button"):

        result = calculate_two_independent_means(
            alpha,
            power,
            sd,
            delta,
            two_sided,
            dropout_rate,
            allocation_ratio
        )

        Z_alpha = stats.norm.ppf(1 - alpha/2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")

        st.success(f"Group 1 Sample Size: {result['n1']}")
        st.success(f"Group 2 Sample Size: {result['n2']}")

        paragraph = paragraph_two_independent_means(
            alpha,
            power,
            sd,
            delta,
            two_sided,
            dropout_rate,
            result["n1"],
            result["n2"]
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

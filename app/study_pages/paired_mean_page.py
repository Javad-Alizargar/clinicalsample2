# ==========================================
# Paired Mean — Modular Advanced Version
# ==========================================

import streamlit as st
import scipy.stats as stats
import math

from calculators.continuous.paired_mean import calculate_paired_mean
from templates.paragraph_templates import paragraph_paired_mean

from app.components.stat_extraction import render_sd_extraction_section
from app.components.pubmed_section import render_pubmed_section


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):

    st.header("Paired Mean — Before–After / Matched Design")

    # ==========================================================
    # Study Explanation
    # ==========================================================

    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Used when the same participants are measured twice.

Examples:
• Before vs after treatment  
• Pre-intervention vs post-intervention  
• Matched case-control pairs  

Key difference from independent design:
We analyze the mean of paired differences.

Required:
• SD of paired differences  
• Mean difference (Δ)
        """)

    # ==========================================================
    # Formula
    # ==========================================================

    with st.expander("📐 Mathematical Formula", expanded=True):

        st.latex(r"""
        n =
        \left(
        \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD_{diff}}
        {\Delta}
        \right)^2
        """)

    # ==========================================================
    # OPTION 1 — Direct SD of Differences
    # ==========================================================

    with st.expander("🧮 Option 1: Use Reported SD of Differences", expanded=False):

        st.info("Use this if paper directly reports SD of change.")

        sd_diff_direct = st.number_input(
            "SD of Paired Differences",
            min_value=0.0001,
            value=5.0,
            key="paired_sd_direct"
        )

    # ==========================================================
    # OPTION 2 — Derive SD of Differences
    # ==========================================================

    with st.expander("🧮 Option 2: Derive SD of Differences from SD1, SD2, Correlation", expanded=False):

        st.markdown("Formula:")

        st.latex(r"""
        SD_{diff} =
        \sqrt{
        SD_1^2 + SD_2^2 - 2\rho SD_1 SD_2
        }
        """)

        sd1 = st.number_input("SD Before", min_value=0.0001, value=10.0, key="paired_sd1")
        sd2 = st.number_input("SD After", min_value=0.0001, value=10.0, key="paired_sd2")
        rho = st.slider("Correlation (ρ)", 0.0, 0.99, 0.5, key="paired_rho")

        if st.button("Compute SD_diff", key="paired_compute_sd"):

            sd_diff_calc = math.sqrt(sd1**2 + sd2**2 - 2*rho*sd1*sd2)
            st.success(f"Derived SD_diff = {round(sd_diff_calc,4)}")

    # ==========================================================
    # Δ Helper
    # ==========================================================

    with st.expander("📊 Compute Mean Difference (Δ)", expanded=False):

        mean_before = st.number_input("Mean Before", value=120.0, key="paired_mean1")
        mean_after = st.number_input("Mean After", value=110.0, key="paired_mean2")

        if st.button("Compute Δ", key="paired_delta_button"):
            delta_calc = abs(mean_after - mean_before)
            st.success(f"Δ = {round(delta_calc,4)}")

    # ==========================================================
    # SD Extraction Helper (optional reuse)
    # ==========================================================

    render_sd_extraction_section(prefix="paired")

    # ==========================================================
    # PubMed Helper
    # ==========================================================

    render_pubmed_section(
        study_type="Paired Mean",
        default_outcome="blood pressure",
        default_population="before after study",
        default_extra="standard deviation OR change score",
        key_prefix="paired_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final Planning
    # ==========================================================

    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    sd_final = st.number_input(
        "SD of Differences for Planning",
        min_value=0.0001,
        value=5.0,
        key="paired_final_sd"
    )

    delta = st.number_input(
        "Mean difference (Δ)",
        min_value=0.0001,
        value=5.0,
        key="paired_final_delta"
    )

    if st.button("Calculate Sample Size", key="paired_calc_button"):

        delta_used = abs(delta)

        result = calculate_paired_mean(
            alpha,
            power,
            sd_final,
            delta_used,
            two_sided,
            dropout_rate
        )

        Z_alpha = stats.norm.ppf(1 - alpha/2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")

        st.success(f"Required Sample Size: {result['n_required']}")
        st.write("Before dropout adjustment:", result["n_before_dropout"])

        paragraph = paragraph_paired_mean(
            alpha,
            power,
            sd_final,
            delta_used,
            two_sided,
            dropout_rate,
            result["n_required"]
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

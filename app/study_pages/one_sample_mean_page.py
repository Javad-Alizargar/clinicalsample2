# ==========================================
# One-Sample Mean — Modular Version
# Uses reusable SD extraction + PubMed component
# ==========================================

import streamlit as st
import scipy.stats as stats

from calculators.continuous.one_sample_mean import calculate_one_sample_mean
from templates.paragraph_templates import paragraph_one_sample_mean

# Reusable components
from app.components.stat_extraction import render_sd_extraction_section
from app.components.pubmed_section import render_pubmed_section


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):

    st.header("One-Sample Mean — Advanced Sample Size Planning")

    # ==========================================================
    # Concept
    # ==========================================================

    with st.expander("📘 What is One-Sample Mean Design?", expanded=True):
        st.markdown("""
This design compares one group mean to a known or reference value.

Examples:
• Is fasting glucose different from 100 mg/dL?
• Is mean LDL below treatment threshold?
• Is biomarker level different from historical norm?

Planning requires:
• Standard deviation (SD)
• Clinically meaningful difference (Δ)
        """)

    # ==========================================================
    # Formula
    # ==========================================================

    with st.expander("📐 Mathematical Formula", expanded=True):

        st.latex(r"""
        n = \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD}{\Delta} \right)^2
        """)

        st.markdown("""
Two-sided:
Zα = Φ⁻¹(1 − α/2)

One-sided:
Zα = Φ⁻¹(1 − α)
        """)

    # ==========================================================
    # Reusable SD Extraction Component
    # ==========================================================

    render_sd_extraction_section(prefix="one_sample")

    # ==========================================================
    # Compute Δ helper
    # ==========================================================

    with st.expander("📊 Compute Clinically Meaningful Δ", expanded=False):

        mean1 = st.number_input("Sample mean", value=110.0, key="delta_mean1")
        ref = st.number_input("Reference value", value=100.0, key="delta_ref")

        if st.button("Compute Δ", key="delta_button"):
            delta_calc = abs(mean1 - ref)
            st.success(f"Δ = {round(delta_calc,4)}")

    # ==========================================================
    # Reusable PubMed Component
    # ==========================================================

    render_pubmed_section(
        study_type="One-Sample Mean",
        default_outcome="fasting glucose",
        default_population="type 2 diabetes",
        default_extra="standard deviation OR mean",
        key_prefix="one_sample_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final Sample Size Calculation
    # ==========================================================

    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    sd = st.number_input(
        "Standard Deviation (SD) for planning",
        min_value=0.0001,
        value=15.0,
        key="final_sd"
    )

    delta = st.number_input(
        "Clinically meaningful Δ",
        min_value=0.0001,
        value=10.0,
        key="final_delta"
    )

    if st.button("Calculate Sample Size", key="final_calc_button"):

        result = calculate_one_sample_mean(
            alpha,
            power,
            sd,
            delta,
            two_sided,
            dropout_rate
        )

        Z_alpha = stats.norm.ppf(1 - alpha/2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")

        st.success(f"Required Sample Size (adjusted): {result['n_required']}")
        st.write("Before dropout adjustment:", result["n_before_dropout"])

        paragraph = paragraph_one_sample_mean(
            alpha,
            power,
            sd,
            delta,
            two_sided,
            dropout_rate,
            result["n_required"]
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

# ==========================================
# One-Sample Mean — Isolated Page Module (Option B)
# Uses reusable PubMed component
# ==========================================
import streamlit as st
import scipy.stats as stats

from calculators.continuous.one_sample_mean import calculate_one_sample_mean
from templates.paragraph_templates import paragraph_one_sample_mean

# Reusable PubMed component
from app.components.pubmed_section import render_pubmed_section


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):

    st.header("One-Sample Mean")

    # ==========================
    # When to Use
    # ==========================
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when comparing a sample mean to a known or reference value.

Typical inputs needed from literature or pilot study:
- SD (standard deviation)
- Reference mean (if relevant)
- Clinically meaningful difference (Δ)
        """)

    # ==========================
    # Formula
    # ==========================
    with st.expander("📐 Formula", expanded=True):
        st.latex(r"""
        n = \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD}{\Delta} \right)^2
        """)
        st.caption("Two-sided: Zα = Φ⁻¹(1-α/2) | One-sided: Zα = Φ⁻¹(1-α)")

    # ==========================
    # PubMed Reusable Section
    # ==========================
    render_pubmed_section(
        study_type="One-Sample Mean",
        default_outcome="fasting glucose",
        default_population="type 2 diabetes",
        default_extra="standard deviation",
        key_prefix="one_sample",
        expanded=False
    )

    # ==========================
    # Calculation Section
    # ==========================
    st.markdown("---")
    st.subheader("🎯 Sample Size Calculation")

    sd = st.number_input(
        "Standard Deviation (SD)",
        min_value=0.0001,
        value=1.0
    )

    delta = st.number_input(
        "Clinically Meaningful Difference (Δ)",
        min_value=0.0001,
        value=0.5
    )

    if st.button("Calculate Sample Size"):

        result = calculate_one_sample_mean(
            alpha,
            power,
            sd,
            delta,
            two_sided,
            dropout_rate
        )

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha / 2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")

        st.write(f"Zα = {Z_alpha:.4f}")
        st.write(f"Zβ = {Z_beta:.4f}")

        st.latex(rf"""
        n = \left( \frac{{({Z_alpha:.4f} + {Z_beta:.4f}) \cdot {sd}}}{{{delta}}} \right)^2
        """)

        st.success(f"Required Sample Size (adjusted for dropout): {result['n_required']}")
        st.write("Before dropout adjustment:", result["n_before_dropout"])

        st.markdown("### 📄 Paragraph for Methods Section")

        paragraph = paragraph_one_sample_mean(
            alpha,
            power,
            sd,
            delta,
            two_sided,
            dropout_rate,
            result["n_required"]
        )

        st.code(paragraph)

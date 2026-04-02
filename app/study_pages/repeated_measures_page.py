# app/study_pages/repeated_measures_page.py

import streamlit as st
import scipy.stats as stats

from calculators.continuous.repeated_measures import calculate_repeated_measures
from templates.paragraph_templates import paragraph_repeated_measures
from app.components.stat_extraction import render_sd_extraction_section
from app.components.pubmed_section import render_pubmed_section

def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("Multiple Measurements (Repeated Measures)")

    # ==========================================================
    # Concept
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Used when the same subjects are measured multiple times (longitudinal design) and you want to compare two independent groups (e.g., Treatment vs. Control).

Because subjects act as their own controls, repeated measurements are correlated. This correlation (ρ) allows you to use a smaller sample size than a standard cross-sectional study.

**Two Primary Scenarios:**
* **Scenario A (Average):** Are the groups different on average across *all* time points?
* **Scenario B (Change Over Time):** Do the groups *change* differently over time? (e.g., Treatment improves faster than Control).
        """)

    # ==========================================================
    # Formulas
    # ==========================================================
    with st.expander("📐 Mathematical Formulas", expanded=False):
        st.markdown("First, we calculate the standard cross-sectional sample size ($N_{std}$). Then we apply an adjustment factor:")
        st.markdown("**Scenario A (Overall Average Difference):**")
        st.latex(r"N_{rep} = N_{std} \times \frac{1 + (m - 1)\rho}{m}")
        st.markdown("**Scenario B (Change Over Time / Interaction):**")
        st.latex(r"N_{rep} = N_{std} \times (1 - \rho)")

    # ==========================================================
    # Helpers
    # ==========================================================
    render_sd_extraction_section(prefix="rep_meas")
    
    render_pubmed_section(
        study_type="Repeated Measures",
        default_outcome="biomarker levels",
        default_population="longitudinal cohort",
        default_extra="repeated measures OR longitudinal OR intra-class correlation",
        key_prefix="rep_meas_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final Calculation
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    scenario_label = st.radio(
        "Study Objective",
        ["Scenario A: Compare the overall average between groups", 
         "Scenario B: Compare the change over time (Interaction)"],
        key="rm_scenario"
    )
    scenario = "average" if "Scenario A" in scenario_label else "interaction"

    col1, col2 = st.columns(2)
    with col1:
        m = st.number_input("Number of measurements per subject (m)", min_value=2, value=3, step=1, key="rm_m")
        sd = st.number_input("Standard Deviation (SD) at a single time point", min_value=0.0001, value=15.0, key="rm_sd")
    with col2:
        rho = st.slider("Correlation between repeated measures (ρ)", 0.0, 0.99, 0.50, step=0.05, key="rm_rho")
        delta = st.number_input("Mean difference to detect (Δ)", min_value=0.0001, value=10.0, key="rm_delta")

    allocation_ratio = st.number_input("Allocation ratio (n2/n1)", min_value=0.1, value=1.0, key="rm_ratio")

    if st.button("Calculate Sample Size", key="rm_calc_button"):
        result = calculate_repeated_measures(
            alpha, power, sd, delta, int(m), rho, scenario, allocation_ratio, two_sided, dropout_rate
        )

        Z_alpha = stats.norm.ppf(1 - alpha/2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha, 4)}")
        st.write(f"Zβ = {round(Z_beta, 4)}")
        st.write(f"**Adjustment Factor applied:** {result['adjustment_factor']}")

        st.success(f"Group 1 Required: {result['n_group1']}")
        st.success(f"Group 2 Required: {result['n_group2']}")
        st.write("Total Sample Size:", result["n_total"])

        paragraph = paragraph_repeated_measures(
            alpha, power, sd, delta, int(m), rho, scenario, allocation_ratio, two_sided, dropout_rate,
            result['n_group1'], result['n_group2']
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

# ==========================================
# One-Sample Mean — Advanced Planning Module
# ==========================================

import streamlit as st
import scipy.stats as stats
import math

from calculators.continuous.one_sample_mean import calculate_one_sample_mean
from templates.paragraph_templates import paragraph_one_sample_mean
from utils.pubmed_utils import build_pubmed_query, search_pubmed, fetch_pubmed_details, throttle_sleep


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):

    st.header("One-Sample Mean — Advanced Sample Size Planning")

    # ==========================================================
    # Concept
    # ==========================================================

    with st.expander("📘 What is One-Sample Mean Design?", expanded=True):
        st.markdown("""
Used when comparing a single group mean to a known reference value.

Examples:
• Is mean fasting glucose different from 100 mg/dL?
• Is average LDL below guideline threshold?
• Is mean biomarker level different from historical norm?

Required inputs:
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
    # Extract SD Section
    # ==========================================================

    with st.expander("🧠 Extract SD from Common Abstract Statistics", expanded=True):

        tab1, tab2, tab3 = st.tabs([
            "SD from 95% CI",
            "SD from SE",
            "SD from IQR"
        ])

        # -----------------------------
        # SD from CI
        # -----------------------------
        with tab1:

            mean_ci = st.number_input("Mean (optional)", value=100.0, key="ci_mean")
            lower = st.number_input("CI lower", value=95.0, key="ci_lower")
            upper = st.number_input("CI upper", value=105.0, key="ci_upper")
            n_ci = st.number_input("Sample size (n)", min_value=2, value=50, key="ci_n")

            if st.button("Compute SD from CI", key="ci_button"):
                Z = 1.96
                se = (upper - lower) / (2 * Z)
                sd = se * math.sqrt(n_ci)
                st.success(f"Estimated SD ≈ {round(sd,4)}")

        # -----------------------------
        # SD from SE
        # -----------------------------
        with tab2:

            se_val = st.number_input("Standard Error (SE)", value=2.0, key="se_value")
            n_se = st.number_input("Sample size (n)", min_value=2, value=50, key="se_n")

            if st.button("Compute SD from SE", key="se_button"):
                sd = se_val * math.sqrt(n_se)
                st.success(f"Estimated SD ≈ {round(sd,4)}")

        # -----------------------------
        # SD from IQR
        # -----------------------------
        with tab3:

            iqr = st.number_input("IQR (Q3 − Q1)", value=10.0, key="iqr_value")

            if st.button("Approximate SD from IQR", key="iqr_button"):
                sd = iqr / 1.35
                st.success(f"Approximate SD ≈ {round(sd,4)}")

    # ==========================================================
    # Compute Δ
    # ==========================================================

    with st.expander("📊 Compute Δ from Means", expanded=False):

        mean1 = st.number_input("Sample mean", value=110.0, key="delta_mean1")
        ref = st.number_input("Reference value", value=100.0, key="delta_ref")

        if st.button("Compute Δ", key="delta_button"):
            delta_calc = abs(mean1 - ref)
            st.success(f"Δ = {round(delta_calc,4)}")

    # ==========================================================
    # PubMed
    # ==========================================================

    with st.expander("🔎 PubMed Literature Search", expanded=False):

        col1, col2 = st.columns(2)
        with col1:
            outcome = st.text_input("Outcome", value="fasting glucose", key="pub_outcome")
        with col2:
            population = st.text_input("Population", value="type 2 diabetes", key="pub_population")

        extra = st.text_input("Extra keywords", value="standard deviation OR mean", key="pub_extra")

        suggested = build_pubmed_query(
            "One-Sample Mean",
            outcome=outcome,
            population=population,
            extra=extra
        )

        query = st.text_input("PubMed query", value=suggested, key="pub_query")

        retmax = st.slider("Number of studies", 5, 100, 50, 5, key="pub_retmax")

        api_key = st.text_input("NCBI API key (optional)", type="password", key="pub_api").strip() or None

        if st.button("Search PubMed", key="pub_search_button"):

            try:
                pmids = search_pubmed(query=query, retmax=retmax, sort="relevance", api_key=api_key)
                throttle_sleep(1, api_key=api_key)

                if not pmids:
                    st.warning("No results found.")
                else:
                    articles = fetch_pubmed_details(pmids, api_key=api_key)
                    throttle_sleep(1, api_key=api_key)

                    st.success(f"Found {len(articles)} studies")

                    for a in articles:
                        st.markdown(f"**[{a.title}]({a.url})**")
                        meta = " • ".join(filter(None, [a.journal, a.year, a.authors]))
                        st.caption(meta)

                        if a.abstract:
                            with st.expander("Abstract"):
                                st.write(a.abstract)

                        st.markdown("---")

            except Exception as e:
                st.error(str(e))

    # ==========================================================
    # Final Calculation
    # ==========================================================

    st.markdown("---")
    st.subheader("🎯 Final Sample Size")

    sd = st.number_input("SD for planning", min_value=0.0001, value=15.0, key="final_sd")
    delta = st.number_input("Δ for planning", min_value=0.0001, value=10.0, key="final_delta")

    if st.button("Calculate Sample Size", key="final_calc_button"):

        result = calculate_one_sample_mean(alpha, power, sd, delta, two_sided, dropout_rate)

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

        st.code(paragraph)

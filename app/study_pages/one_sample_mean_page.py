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
    # SECTION 1 — Conceptual Explanation
    # ==========================================================

    with st.expander("📘 What is One-Sample Mean Design?", expanded=True):
        st.markdown("""
This design is used when:

• You have **one group**
• You want to compare its mean to a known/reference value

Examples:
- Is mean fasting glucose different from 100 mg/dL?
- Is mean LDL lower than guideline threshold?
- Is average pain score different from historical data?

Statistical test:
One-sample t-test (large sample → z approximation)

Key planning inputs:
1) SD (standard deviation of outcome)
2) Clinically meaningful difference (Δ)
        """)

    # ==========================================================
    # SECTION 2 — Formula
    # ==========================================================

    with st.expander("📐 Mathematical Formula", expanded=True):

        st.latex(r"""
        n = \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD}{\Delta} \right)^2
        """)

        st.markdown("""
Where:

- SD = standard deviation
- Δ = clinically meaningful difference
- Zα = critical value from α
- Zβ = critical value from power

Two-sided:
Zα = Φ⁻¹(1 − α/2)

One-sided:
Zα = Φ⁻¹(1 − α)
        """)

    # ==========================================================
    # SECTION 3 — HOW TO EXTRACT SD FROM PAPERS
    # ==========================================================

    with st.expander("🧠 Extract SD from Common Abstract Statistics", expanded=True):

        tab1, tab2, tab3 = st.tabs([
            "SD from 95% CI",
            "SD from Standard Error (SE)",
            "SD from IQR (approximate)"
        ])

        # -----------------------------
        # SD from CI
        # -----------------------------
        with tab1:
            st.markdown("""
If a paper reports:

Mean = 120 (95% CI 115–125)

Then:

SE = (Upper − Lower) / (2 × Z₀.₉₇₅)

SD = SE × √n
            """)

            mean_ci = st.number_input("Mean (optional)", value=100.0)
            lower = st.number_input("CI lower", value=95.0)
            upper = st.number_input("CI upper", value=105.0)
            n_ci = st.number_input("Sample size (n)", min_value=2, value=50)

            if st.button("Compute SD from CI"):
                Z = 1.96
                se = (upper - lower) / (2 * Z)
                sd = se * math.sqrt(n_ci)

                st.success(f"Estimated SD ≈ {round(sd,4)}")

        # -----------------------------
        # SD from SE
        # -----------------------------
        with tab2:
            st.markdown("""
If a paper reports:

Mean ± SE

Then:

SD = SE × √n
            """)

            se_val = st.number_input("Standard Error (SE)", value=2.0)
            n_se = st.number_input("Sample size (n)", min_value=2, value=50)

            if st.button("Compute SD from SE"):
                sd = se_val * math.sqrt(n_se)
                st.success(f"Estimated SD ≈ {round(sd,4)}")

        # -----------------------------
        # SD from IQR
        # -----------------------------
        with tab3:
            st.markdown("""
If median and IQR are reported:

Approximation (normal assumption):

SD ≈ IQR / 1.35
            """)

            iqr = st.number_input("IQR (Q3 − Q1)", value=10.0)

            if st.button("Approximate SD from IQR"):
                sd = iqr / 1.35
                st.success(f"Approximate SD ≈ {round(sd,4)}")

    # ==========================================================
    # SECTION 4 — Compute Δ from literature
    # ==========================================================

    with st.expander("📊 Compute Clinically Meaningful Δ from Two Means", expanded=False):

        st.markdown("""
If literature reports:

Mean sample = 110  
Reference value = 100  

Then:

Δ = |110 − 100| = 10
        """)

        mean1 = st.number_input("Sample mean", value=110.0)
        ref = st.number_input("Reference value", value=100.0)

        if st.button("Compute Δ"):
            delta_calc = abs(mean1 - ref)
            st.success(f"Δ = {round(delta_calc,4)}")

    # ==========================================================
    # SECTION 5 — PubMed Helper
    # ==========================================================

    with st.expander("🔎 PubMed Literature Search Helper", expanded=False):

        col1, col2 = st.columns(2)
        with col1:
            outcome = st.text_input("Outcome / biomarker", value="fasting glucose")
        with col2:
            population = st.text_input("Population", value="type 2 diabetes")

        extra = st.text_input("Extra keywords", value="standard deviation OR mean")

        suggested = build_pubmed_query(
            "One-Sample Mean",
            outcome=outcome,
            population=population,
            extra=extra
        )

        query = st.text_input("PubMed query", value=suggested)

        retmax = st.slider("Number of studies", 5, 100, 50, 5)

        api_key = st.text_input("NCBI API key (optional)", type="password").strip() or None

        if st.button("Search PubMed"):
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
    # SECTION 6 — Final Sample Size
    # ==========================================================

    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    sd = st.number_input("SD for planning", min_value=0.0001, value=15.0)
    delta = st.number_input("Clinically meaningful Δ", min_value=0.0001, value=10.0)

    if st.button("Calculate Sample Size"):

        result = calculate_one_sample_mean(alpha, power, sd, delta, two_sided, dropout_rate)

        Z_alpha = stats.norm.ppf(1 - alpha/2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.markdown("### Intermediate values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")

        st.latex(rf"""
        n = \left(
        \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)}) \cdot {sd}}}
        {{{delta}}}
        \right)^2
        """)

        st.success(f"Required Sample Size (adjusted): {result['n_required']}")
        st.write("Before dropout adjustment:", result["n_before_dropout"])

        st.markdown("### Methods paragraph")
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

# ==========================================
# One-Sample Mean — Isolated Page Module (Option B)
# ==========================================
import streamlit as st
import scipy.stats as stats

from calculators.continuous.one_sample_mean import calculate_one_sample_mean
from templates.paragraph_templates import paragraph_one_sample_mean

from utils.pubmed_utils import build_pubmed_query, search_pubmed, fetch_pubmed_details, throttle_sleep


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("One-Sample Mean")

    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when comparing a sample mean to a known or reference value.

Typical inputs needed from literature/pilot:
- SD (standard deviation)
- Reference mean (if relevant)
- Clinically meaningful difference (Δ)
        """)

    with st.expander("📐 Formula", expanded=True):
        st.latex(r"n = \left( \frac{(Z_{\alpha} + Z_{\beta}) \cdot SD}{\Delta} \right)^2")
        st.caption("Two-sided uses Zα = Φ⁻¹(1-α/2); one-sided uses Zα = Φ⁻¹(1-α).")

    with st.expander("🔎 PubMed helper (find SD / baseline / Δ clues)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            outcome = st.text_input("Outcome / biomarker", value="fasting glucose")
        with col2:
            population = st.text_input("Population", value="type 2 diabetes")

        extra = st.text_input("Extra keywords (optional)", value="standard deviation")

        suggested = build_pubmed_query("One-Sample Mean", outcome=outcome, population=population, extra=extra)
        query = st.text_input("PubMed query (editable)", value=suggested)

        retmax = st.slider("Results", 5, 30, 12, 1)
        api_key = st.text_input("NCBI API key (optional)", value="", type="password").strip() or None

        if st.button("Search PubMed"):
            try:
                pmids = search_pubmed(query=query, retmax=retmax, sort="relevance", api_key=api_key)
                throttle_sleep(1, api_key=api_key)

                if not pmids:
                    st.warning("No results found. Try broader keywords.")
                else:
                    articles = fetch_pubmed_details(pmids, api_key=api_key)
                    throttle_sleep(1, api_key=api_key)

                    st.success(f"Found {len(articles)} records.")
                    for a in articles:
                        title_line = a.title if a.title else f"PMID {a.pmid}"
                        st.markdown(f"**[{title_line}]({a.url})**")
                        meta = " • ".join([x for x in [a.journal, a.year, a.authors, (f'DOI: {a.doi}' if a.doi else '')] if x])
                        if meta:
                            st.caption(meta)
                        if a.abstract:
                            with st.expander("Abstract"):
                                st.write(a.abstract)
                        st.markdown("---")
            except Exception as e:
                st.error(f"PubMed search failed: {e}")

    st.markdown("---")
    st.subheader("🎯 Calculation")

    sd = st.number_input("SD", min_value=0.0001, value=1.0)
    delta = st.number_input("Δ (clinically meaningful difference)", min_value=0.0001, value=0.5)

    if st.button("Calculate Sample Size"):
        result = calculate_one_sample_mean(alpha, power, sd, delta, two_sided, dropout_rate)

        Z_alpha = stats.norm.ppf(1 - alpha/2) if two_sided else stats.norm.ppf(1 - alpha)
        Z_beta = stats.norm.ppf(power)

        st.markdown("### Intermediate values")
        st.write(f"Zα = {Z_alpha:.4f}")
        st.write(f"Zβ = {Z_beta:.4f}")

        st.success(f"Required Sample Size (adjusted for dropout): {result['n_required']}")
        st.write("Before dropout adjustment:", result["n_before_dropout"])

        st.markdown("### Paragraph (copy for Methods)")
        paragraph = paragraph_one_sample_mean(alpha, power, sd, delta, two_sided, dropout_rate, result["n_required"])
        st.code(paragraph)

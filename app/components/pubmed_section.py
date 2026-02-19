# ==========================================
# Reusable PubMed UI Section (Component)
# Use inside any study page with:
#   from app.components.pubmed_section import render_pubmed_section
# ==========================================
from __future__ import annotations

import streamlit as st

from utils.pubmed_utils import (
    build_pubmed_query,
    search_pubmed,
    fetch_pubmed_details,
    throttle_sleep,
)

def render_pubmed_section(
    study_type: str,
    default_outcome: str = "",
    default_population: str = "",
    default_extra: str = "",
    key_prefix: str = "pubmed",
    expanded: bool = False,
):
    """
    Reusable PubMed helper UI for extracting planning inputs (SD, event rate, HR, OR, etc.).

    Parameters
    ----------
    study_type : str
        Used by build_pubmed_query to propose a reasonable starting query.
    default_outcome/default_population/default_extra : str
        Prefill boxes for better UX per study type.
    key_prefix : str
        IMPORTANT: must be unique per page to avoid Streamlit widget key collisions.
    expanded : bool
        Whether expander is open by default.
    """
    with st.expander("🔎 PubMed helper (find inputs from literature)", expanded=expanded):

        c1, c2 = st.columns(2)
        with c1:
            outcome = st.text_input(
                "Outcome / biomarker",
                value=default_outcome,
                key=f"{key_prefix}_outcome",
            )
        with c2:
            population = st.text_input(
                "Population",
                value=default_population,
                key=f"{key_prefix}_population",
            )

        extra = st.text_input(
            "Extra keywords (optional)",
            value=default_extra,
            key=f"{key_prefix}_extra",
        )

        suggested = build_pubmed_query(
            study_type=study_type,
            outcome=outcome,
            population=population,
            extra=extra,
        )

        query = st.text_input(
            "PubMed query (editable)",
            value=suggested,
            key=f"{key_prefix}_query",
        )

        retmax = st.slider(
            "Number of studies to retrieve",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            key=f"{key_prefix}_retmax",
        )

        api_key = st.text_input(
            "NCBI API key (optional)",
            value="",
            type="password",
            key=f"{key_prefix}_apikey",
        ).strip() or None

        sort = st.selectbox(
            "Sort",
            options=["relevance", "pub+date"],
            index=0,
            key=f"{key_prefix}_sort",
        )

        if st.button("Search PubMed", key=f"{key_prefix}_search_btn"):
            try:
                pmids = search_pubmed(query=query, retmax=retmax, sort=sort, api_key=api_key)
                throttle_sleep(1, api_key=api_key)

                if not pmids:
                    st.warning("No results found. Try broader keywords or fewer constraints.")
                    return

                articles = fetch_pubmed_details(pmids, api_key=api_key)
                throttle_sleep(1, api_key=api_key)

                st.success(f"Found {len(articles)} records.")

                for a in articles:
                    title_line = a.title if a.title else f"PMID {a.pmid}"
                    st.markdown(f"**[{title_line}]({a.url})**")

                    meta_parts = []
                    if a.journal: meta_parts.append(a.journal)
                    if a.year: meta_parts.append(a.year)
                    if a.authors: meta_parts.append(a.authors)
                    if a.doi: meta_parts.append(f"DOI: {a.doi}")

                    if meta_parts:
                        st.caption(" • ".join(meta_parts))

                    if a.abstract:
                        with st.expander("Abstract", expanded=False):
                            st.write(a.abstract)

                    st.markdown("---")

            except Exception as e:
                st.error(f"PubMed search failed: {e}")

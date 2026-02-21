# ==========================================
# Logistic Regression — Modular Advanced Version
# EPV-based sample size planning
# ==========================================

import streamlit as st
import math

from templates.paragraph_templates import paragraph_logistic_regression_epv
from app.components.pubmed_section import render_pubmed_section


def _adjust_for_dropout(n: int, dropout_rate: float) -> int:
    if dropout_rate < 0:
        dropout_rate = 0.0
    if dropout_rate >= 0.95:
        raise ValueError("Dropout rate too high.")
    return int(math.ceil(n / (1.0 - dropout_rate)))


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("Logistic Regression — Sample Size Planning")

    # ==========================================================
    # Explanation
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Logistic regression models a **binary outcome** using multiple predictors.

Unlike linear regression, sample size planning is commonly based on:

### Events Per Variable (EPV)

EPV ensures model stability rather than hypothesis-test power.

Typical recommendations:
- EPV ≥ 10 (minimum traditional rule)
- EPV ≥ 15–20 (more conservative, modern guidance)

You must know:
- Expected event rate
- Number of predictors in the model
        """)

    # ==========================================================
    # EPV Concept
    # ==========================================================
    with st.expander("📐 EPV Formula", expanded=False):
        st.latex(r"Required\ Events = EPV \times Number\ of\ Predictors")
        st.latex(r"N = \frac{Required\ Events}{Event\ Rate}")
        st.caption("This is a model-stability planning approach, not a hypothesis-test power calculation.")

    # ==========================================================
    # PubMed helper
    # ==========================================================
    render_pubmed_section(
        study_type="Logistic Regression",
        default_outcome="odds ratio",
        default_population="cohort",
        default_extra="logistic regression OR event rate",
        key_prefix="logreg_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final Planning Inputs
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation (EPV Method)")

    event_rate = st.number_input(
        "Expected event rate (0–1)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        step=0.01,
        key="logreg_event_rate"
    )

    n_predictors = st.number_input(
        "Number of predictors in model",
        min_value=1,
        value=5,
        step=1,
        key="logreg_predictors"
    )

    epv = st.selectbox(
        "Events per variable (EPV)",
        [10, 15, 20, 25],
        index=1,
        key="logreg_epv"
    )

    if st.button("Calculate Sample Size", key="logreg_calc_btn"):

        if event_rate <= 0:
            st.error("Event rate must be > 0.")
            st.stop()

        required_events = int(epv) * int(n_predictors)
        n_raw = math.ceil(required_events / event_rate)
        n_final = _adjust_for_dropout(n_raw, dropout_rate)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Required events = {required_events}")
        st.write(f"Raw sample size = {n_raw}")

        st.success(f"Required sample size (after dropout): {n_final}")
        st.write("Before dropout adjustment:", n_raw)

        paragraph = paragraph_logistic_regression_epv(
            event_rate=event_rate,
            n_predictors=int(n_predictors),
            epv=int(epv),
            dropout_rate=dropout_rate,
            n_required=n_final,
            required_events=required_events
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

    # ==========================================================
    # Educational Note
    # ==========================================================
    with st.expander("📚 Important Note", expanded=False):
        st.markdown("""
This EPV approach ensures model stability.

If your goal is to detect a specific odds ratio with statistical power,
a Wald-test based power model is required instead.
That can be added as an advanced mode later.
        """)
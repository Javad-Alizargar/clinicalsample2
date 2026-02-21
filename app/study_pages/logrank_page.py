# ==========================================
# Survival (Log-Rank) — Modular Advanced Version
# ==========================================

import streamlit as st
import math

from calculators.survival.logrank import calculate_logrank  # you should already have this; if not, tell me
from templates.paragraph_templates import paragraph_logrank
from app.components.pubmed_section import render_pubmed_section


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("Survival (Log-Rank) — Sample Size Planning")

    # ==========================================================
    # Explanation
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Use when comparing **time-to-event** outcomes between **two groups**.

Examples:
- Overall survival: treatment vs control
- Time to relapse: intervention vs standard care
- Time to hospitalization: exposed vs unexposed

Planning typically uses:
- **Hazard Ratio (HR)** you want to detect
- **Allocation ratio** (n2/n1)
- **Event fraction** (expected proportion with event during follow-up)

Key idea:
- Log-rank power depends primarily on the **number of events**, not just total N.
        """)

    # ==========================================================
    # Formula concept
    # ==========================================================
    with st.expander("📐 Key Concepts", expanded=False):
        st.markdown("### Required events (core quantity)")
        st.latex(r"E \approx \frac{(Z_{\alpha} + Z_{\beta})^2}{(\log(HR))^2 \cdot p_1 p_2}")
        st.caption("Where p1 and p2 are group proportions (determined by allocation ratio).")

        st.markdown("### Convert events to total N")
        st.latex(r"N \approx \frac{E}{Event\ Fraction}")
        st.caption("Event fraction = expected % with event during follow-up (can be estimated from literature).")

    # ==========================================================
    # PubMed helper
    # ==========================================================
    render_pubmed_section(
        study_type="Survival (Log-Rank)",
        default_outcome="overall survival hazard ratio",
        default_population="randomized trial",
        default_extra="hazard ratio OR log-rank OR survival",
        key_prefix="logrank_pubmed",
        expanded=False
    )

    # ==========================================================
    # Inputs
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    hazard_ratio = st.number_input(
        "Target hazard ratio (HR)",
        min_value=0.01,
        value=0.75,
        step=0.01,
        key="lr_hr"
    )

    allocation_ratio = st.number_input(
        "Allocation ratio (n2/n1)",
        min_value=0.1,
        value=1.0,
        step=0.1,
        key="lr_ratio"
    )

    event_fraction = st.number_input(
        "Expected event fraction during follow-up (0–1)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.50,
        step=0.01,
        key="lr_event_fraction"
    )

    if st.button("Calculate Sample Size", key="lr_calc_btn"):

        if dropout_rate >= 0.95:
            st.error("Dropout rate too high. Please use < 0.95.")
            st.stop()

        if hazard_ratio <= 0:
            st.error("HR must be > 0.")
            st.stop()

        if hazard_ratio == 1.0:
            st.error("HR cannot be 1.0 (no effect).")
            st.stop()

        if event_fraction <= 0 or event_fraction >= 1:
            st.error("Event fraction must be between 0 and 1 (exclusive).")
            st.stop()

        # Core calculator
        result = calculate_logrank(
            alpha=alpha,
            power=power,
            hazard_ratio=hazard_ratio,
            allocation_ratio=allocation_ratio,
            event_fraction=event_fraction,
            two_sided=two_sided,
            dropout_rate=dropout_rate
        )

        # Expected keys:
        # n_group1, n_group2, n_total, required_events
        n1 = result["n_group1"]
        n2 = result["n_group2"]
        n_total = result["n_total"]
        required_events = result["required_events"]

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"log(HR) = {math.log(hazard_ratio):.4f}")
        st.write(f"Required events = {required_events}")

        st.success(f"Group 1 required: {n1}")
        st.success(f"Group 2 required: {n2}")
        st.write("Total sample size:", n_total)

        paragraph = paragraph_logrank(
            alpha=alpha,
            power=power,
            hazard_ratio=hazard_ratio,
            allocation_ratio=allocation_ratio,
            event_fraction=event_fraction,
            two_sided=two_sided,
            dropout_rate=dropout_rate,
            n1=n1,
            n2=n2,
            n_total=n_total,
            required_events=required_events
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

    # ==========================================================
    # Practical guidance
    # ==========================================================
    with st.expander("📊 Practical Guidance (How to get event fraction)", expanded=False):
        st.markdown("""
Ways to estimate event fraction:
- If a paper reports 1-year event rate (e.g., 40%), you can use 0.40 (approx) for similar follow-up.
- If you have median survival and follow-up duration, event fraction can be approximated, but it's noisy.
- When uncertain, use a conservative smaller event fraction (smaller fraction → larger N).
        """)
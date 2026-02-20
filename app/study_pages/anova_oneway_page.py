# ==========================================
# One-Way ANOVA — Modular Advanced Version
# ==========================================

import streamlit as st
import math

from calculators.continuous.anova_oneway import calculate_anova_oneway
from templates.paragraph_templates import paragraph_anova

from app.components.pubmed_section import render_pubmed_section


def _allocate_by_weights(total_n: int, weights):
    k = len(weights)
    wsum = sum(weights)
    if wsum <= 0:
        return [math.ceil(total_n / k) for _ in range(k)]

    raw = [total_n * (w / wsum) for w in weights]
    base = [int(math.floor(r)) for r in raw]
    remainder = total_n - sum(base)

    frac = [(raw[i] - base[i], i) for i in range(k)]
    frac.sort(reverse=True)

    for j in range(remainder):
        base[frac[j][1]] += 1

    return base


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):

    st.header("One-Way ANOVA — k Independent Groups (Advanced)")

    # ==========================================================
    # Study Explanation
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Use when comparing a continuous outcome across 3 or more independent groups.

Planning is typically based on Cohen’s f (effect size).
        """)

    # ==========================================================
    # Effect Size Builder
    # ==========================================================
    st.subheader("🧠 Build / Derive Cohen’s f")

    tab_f, tab_means, tab_eta2 = st.tabs([
        "A) Enter f directly",
        "B) From means + SD",
        "C) From η²"
    ])

    with tab_f:
        st.number_input(
            "Cohen’s f",
            min_value=0.0001,
            value=0.25,
            step=0.01,
            key="anova_f_direct"
        )

    with tab_means:
        k_means = st.number_input("Number of groups (k)", min_value=2, value=3, step=1, key="anova_k_means")
        means = []
        for i in range(int(k_means)):
            means.append(st.number_input(f"Mean group {i+1}", value=0.0, key=f"anova_mean_{i}"))

        sd_within = st.number_input("Within-group SD", min_value=0.0001, value=1.0, key="anova_sd_within")

        if st.button("Compute f from means", key="anova_compute_f_means"):
            grand = sum(means) / len(means)
            var_mu = sum((m - grand) ** 2 for m in means) / len(means)
            f_calc = math.sqrt(var_mu) / sd_within
            st.success(f"Cohen’s f = {round(f_calc,4)}")

    with tab_eta2:
        eta2 = st.number_input("η² (0–0.99)", min_value=0.0001, max_value=0.99, value=0.06, step=0.01, key="anova_eta2")

        if st.button("Compute f from η²", key="anova_compute_f_eta2"):
            f_eta = math.sqrt(eta2 / (1 - eta2))
            st.success(f"Cohen’s f = {round(f_eta,4)}")

    # ==========================================================
    # PubMed Helper
    # ==========================================================
    render_pubmed_section(
        study_type="One-Way ANOVA",
        default_outcome="pain score",
        default_population="randomized trial",
        default_extra="ANOVA eta squared OR means standard deviation",
        key_prefix="anova_pubmed",
        expanded=False
    )

    # ==========================================================
    # Unequal Allocation Planner
    # ==========================================================
    with st.expander("⚖️ Optional: Unequal allocation", expanded=False):

        use_weights = st.checkbox("Use unequal allocation weights", value=False, key="anova_use_weights")

        k_weights = st.number_input("k for weights", min_value=2, value=3, step=1, key="anova_k_weights")

        weights = []
        for i in range(int(k_weights)):
            weights.append(st.number_input(f"w{i+1}", min_value=0.0, value=1.0, step=0.1, key=f"anova_w_{i}"))

    # ==========================================================
    # Final Planning
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    k = st.number_input("Number of groups (k)", min_value=2, value=3, step=1, key="anova_k_final")

    f_plan = st.number_input(
        "Cohen’s f for planning",
        min_value=0.0001,
        value=0.25,
        step=0.01,
        key="anova_f_plan"
    )

    if st.button("Calculate ANOVA Sample Size", key="anova_calc_button"):

        if dropout_rate >= 0.95:
            st.error("Dropout rate too high.")
            st.stop()

        # 🔥 IMPORTANT FIX — positional arguments only
        result = calculate_anova_oneway(
            alpha,
            power,
            f_plan,
            int(k),
            dropout_rate
        )

        total_n = int(result["n_total"])
        per_group = int(result["n_per_group"])

        st.success(f"Total N (after dropout): {total_n}")
        st.write(f"Balanced per-group N: {per_group}")

        if st.session_state.get("anova_use_weights", False):
            if int(st.session_state.get("anova_k_weights", k)) == int(k):
                alloc = _allocate_by_weights(total_n, weights)
                st.markdown("### Allocation by weights")
                for i, n_i in enumerate(alloc, start=1):
                    st.write(f"Group {i}: {n_i}")
            else:
                st.warning("Weights k does not match ANOVA k.")

        paragraph = paragraph_anova(
            alpha,
            power,
            f_plan,
            int(k),
            dropout_rate,
            total_n,
            per_group
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

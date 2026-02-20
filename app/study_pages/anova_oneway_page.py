# ==========================================
# One-Way ANOVA — Modular Advanced Version
# Supports effect-size derivation + optional unequal allocation
# ==========================================

import streamlit as st
import math

from calculators.continuous.anova_oneway import calculate_anova_oneway
from templates.paragraph_templates import paragraph_anova

from app.components.pubmed_section import render_pubmed_section


def _safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default


def _allocate_by_weights(total_n: int, weights):
    """
    Allocate integer sample sizes across k groups according to positive weights.
    Ensures sum == total_n using largest remainder.
    """
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
Use when comparing a continuous outcome across **3 or more independent groups**.

Examples:
• LDL cholesterol across 3 diet regimens  
• Pain score across 4 treatment arms  
• Biomarker levels across multiple exposure categories  

ANOVA planning is usually expressed using **Cohen’s f** (effect size).

You can:
• Input f directly  
• Derive f from group means + within-group SD  
• Derive f from η² reported in papers
        """)

    # ==========================================================
    # Formula / Concept
    # ==========================================================
    with st.expander("📐 Key Concepts (Effect Size)", expanded=True):
        st.markdown("### Cohen’s f")
        st.latex(r"f = \sqrt{\frac{\eta^2}{1-\eta^2}}")

        st.markdown("### From group means and within-group SD")
        st.latex(r"\bar{\mu} = \frac{1}{k}\sum_{i=1}^{k}\mu_i")
        st.latex(r"\sigma_{\mu}^2 = \frac{1}{k}\sum_{i=1}^{k}(\mu_i-\bar{\mu})^2")
        st.latex(r"f = \frac{\sqrt{\sigma_{\mu}^2}}{SD_{within}}")

        st.markdown("Heuristics (context-dependent):")
        st.write("• f ≈ 0.10 small")
        st.write("• f ≈ 0.25 medium")
        st.write("• f ≈ 0.40 large")

        st.caption("Note: Your calculator solves N using an F-test power model internally.")

    # ==========================================================
    # Effect Size Builder
    # ==========================================================
    st.subheader("🧠 Build / Derive Cohen’s f (from common abstract stats)")

    tab_f, tab_means, tab_eta2 = st.tabs([
        "A) Enter f directly",
        "B) Compute f from means + SD",
        "C) Compute f from η²"
    ])

    with tab_f:
        f_direct = st.number_input(
            "Cohen’s f",
            min_value=0.0001,
            value=0.25,
            step=0.01,
            key="anova_f_direct"
        )
        st.info("Use this if literature directly reports Cohen’s f, or you have a strong pilot estimate.")

    with tab_means:
        st.markdown("If an abstract reports group means and a common SD (or you assume equal SD), compute f.")
        k_means = st.number_input("Number of groups (k)", min_value=2, value=3, step=1, key="anova_k_means")

        means = []
        for i in range(int(k_means)):
            means.append(st.number_input(f"Mean group {i+1}", value=0.0, key=f"anova_mean_{i}"))

        sd_within = st.number_input("Within-group SD (common SD)", min_value=0.0001, value=1.0, key="anova_sd_within")

        if st.button("Compute f from means", key="anova_compute_f_means"):
            grand = sum(means) / len(means)
            var_mu = sum((m - grand) ** 2 for m in means) / len(means)
            f_calc = math.sqrt(var_mu) / sd_within
            st.success(f"Computed Cohen’s f = {round(f_calc,4)}")
            st.caption("Paste this value into the planning section below if you want to lock it in.")

    with tab_eta2:
        st.markdown("Many papers report η² or partial η². Convert it to Cohen’s f.")
        eta2 = st.number_input("η² (0–0.99)", min_value=0.0001, max_value=0.99, value=0.06, step=0.01, key="anova_eta2")

        if st.button("Compute f from η²", key="anova_compute_f_eta2"):
            f_eta = math.sqrt(eta2 / (1 - eta2))
            st.success(f"Cohen’s f = {round(f_eta,4)}")
            st.caption("Paste this value into the planning section below if you want to lock it in.")

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
    with st.expander("⚖️ Optional: Unequal group allocation (practical planning)", expanded=False):
        st.markdown("""
If your design will not enroll equal numbers per group, you can specify **weights**.

Example (k=3):
• weights = 1, 1, 2 → group3 has twice as many participants.

We compute a total N from the ANOVA model (balanced approximation),
then allocate that N by your weights.

This is a practical planning output; exact power under imbalance may differ slightly.
        """)

        use_weights = st.checkbox("Use unequal allocation weights", value=False, key="anova_use_weights")

        weight_list = []
        k_weights = st.number_input("k for weights (must match your ANOVA k)", min_value=2, value=3, step=1, key="anova_k_weights")

        cols = st.columns(min(int(k_weights), 6))
        for i in range(int(k_weights)):
            col = cols[i % len(cols)]
            with col:
                w = st.number_input(f"w{i+1}", min_value=0.0, value=1.0, step=0.1, key=f"anova_w_{i}")
                weight_list.append(w)

        st.caption("Weights are relative only. All weights must be ≥ 0, and not all zero.")

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
            st.error("Dropout rate too high. Please use < 0.95.")
            st.stop()

        # Use existing calculator (balanced)
        result = calculate_anova_oneway(
            alpha=alpha,
            power=power,
            effect_size=f_plan,
            k_groups=int(k),
            dropout_rate=dropout_rate
        )

        total_n = int(result["n_total"])
        per_group_balanced = int(result["n_per_group"])

        st.success(f"Total N (after dropout adjustment): {total_n}")
        st.write(f"Balanced per-group N (reference): {per_group_balanced}")

        # Allocation by weights (optional)
        if "anova_use_weights" in st.session_state and st.session_state["anova_use_weights"]:
            if int(st.session_state.get("anova_k_weights", k)) != int(k):
                st.warning("Weights k does not match ANOVA k. Using balanced allocation instead.")
            else:
                weights = [float(st.session_state.get(f"anova_w_{i}", 1.0)) for i in range(int(k))]
                if sum(weights) <= 0:
                    st.warning("All weights are zero. Using balanced allocation instead.")
                else:
                    alloc = _allocate_by_weights(total_n, weights)
                    st.markdown("### ⚖️ Unequal Allocation Plan (by weights)")
                    for i, n_i in enumerate(alloc, start=1):
                        st.write(f"Group {i}: {n_i}")
                    st.caption("Power is computed from the ANOVA model; allocation uses your weights as a practical plan.")

        # Methods paragraph
        paragraph = paragraph_anova(
            alpha,
            power,
            f_plan,
            int(k),
            dropout_rate,
            total_n,
            per_group_balanced
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)

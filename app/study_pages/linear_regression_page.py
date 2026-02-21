# ==========================================
# Linear Regression — Modular Advanced Version
# Multiple linear regression sample size planning
# Uses Cohen's f² (power-based) + R² → f² converter
# ==========================================

import streamlit as st
import math
import scipy.stats as stats

from templates.paragraph_templates import paragraph_linear_regression
from app.components.pubmed_section import render_pubmed_section


def _adjust_for_dropout(n: int, dropout_rate: float) -> int:
    if dropout_rate < 0:
        dropout_rate = 0.0
    if dropout_rate >= 0.95:
        raise ValueError("Dropout rate too high.")
    return int(math.ceil(n / (1.0 - dropout_rate)))


def _f2_from_r2(r2: float) -> float:
    r2 = float(r2)
    if r2 <= 0 or r2 >= 1:
        return None
    return r2 / (1.0 - r2)


def _n_for_multiple_regression_f2(alpha: float, power: float, f2: float, u: int) -> int:
    """
    Power for testing overall model (or a block of u predictors) via noncentral F:
      H0: R² = 0 (or ΔR² = 0 for a block)
      F ~ F(u, v, λ), λ = f²*(u+v+1) = f²*(N) (for overall model)
    We solve for minimal v (denominator df) such that power >= target:
      N = u + v + 1
    """
    if u < 1:
        raise ValueError("Number of predictors must be >= 1.")
    if f2 <= 0:
        raise ValueError("f² must be > 0.")

    # Critical F under H0
    fcrit = stats.f.ppf(1 - alpha, u, 1_000_000)  # placeholder v; will be recalculated per loop

    # Search v (denominator df)
    for v in range(1, 200000):
        N = u + v + 1
        # Update fcrit using current v
        fcrit = stats.f.ppf(1 - alpha, u, v)
        lam = f2 * N
        # Power = P(F_{u,v,λ} > fcrit)
        power_now = 1.0 - stats.ncf.cdf(fcrit, u, v, lam)
        if power_now >= power:
            return int(N)

    raise ValueError("Failed to find N within search range. Try larger f² or lower power.")


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("Linear Regression — Sample Size Planning (Multiple Regression)")

    # ==========================================================
    # Explanation
    # ==========================================================
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown("""
Use when your primary analysis is **multiple linear regression** (continuous outcome) with **≥1 predictors**.

Typical planning goal:
- Ensure sufficient N to detect an overall model effect (or a predictor block) using **Cohen’s f²**.

Common inputs from literature/abstracts:
- **R²** (model fit) or **ΔR²** (incremental fit)
- Number of predictors included in the model

This module provides:
- f² planning directly
- R² → f² conversion
- A rule-of-thumb check (non-binding) for model stability
        """)

    # ==========================================================
    # Key concepts
    # ==========================================================
    with st.expander("📐 Key Concepts (f² and R²)", expanded=False):
        st.markdown("### Cohen’s f²")
        st.latex(r"f^2 = \frac{R^2}{1-R^2}")
        st.markdown("Heuristics (context-dependent):")
        st.write("• f² ≈ 0.02 small")
        st.write("• f² ≈ 0.15 medium")
        st.write("• f² ≈ 0.35 large")
        st.caption("Power model uses the noncentral F distribution for multiple regression.")

    # ==========================================================
    # Derive f² from common stats
    # ==========================================================
    st.subheader("🧠 Derive planning effect size from common abstract statistics")

    tab_f2, tab_r2 = st.tabs([
        "A) Enter f² directly",
        "B) Convert from R²"
    ])

    with tab_f2:
        f2_direct = st.number_input(
            "Cohen’s f²",
            min_value=0.0001,
            value=0.15,
            step=0.01,
            key="linreg_f2_direct"
        )
        st.info("Use this if you already have f² (or an assumed effect size) from pilot/literature.")

    with tab_r2:
        st.markdown("If an abstract reports R² for a model, convert to f².")
        r2 = st.number_input("R² (0–0.99)", min_value=0.0, max_value=0.99, value=0.13, step=0.01, key="linreg_r2")
        if st.button("Convert R² → f²", key="linreg_r2_btn"):
            f2 = _f2_from_r2(r2)
            if f2 is None:
                st.error("R² must be between 0 and 1 (non-zero).")
            else:
                st.success(f"f² = {f2:.4f}")
                st.caption("Copy this into the planning section below if you want to lock it in.")

    # ==========================================================
    # PubMed helper
    # ==========================================================
    render_pubmed_section(
        study_type="Linear Regression",
        default_outcome="R squared",
        default_population="cohort",
        default_extra="multiple linear regression R2 OR adjusted R2 OR beta coefficient",
        key_prefix="linreg_pubmed",
        expanded=False
    )

    # ==========================================================
    # Final calculation
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    n_predictors = st.number_input(
        "Number of predictors in the model",
        min_value=1,
        value=5,
        step=1,
        key="linreg_p"
    )

    f2_plan = st.number_input(
        "Effect size f² for planning",
        min_value=0.0001,
        value=0.15,
        step=0.01,
        key="linreg_f2_plan"
    )

    with st.expander("🧪 Optional stability check (rule-of-thumb)", expanded=False):
        per_predictor = st.selectbox(
            "Rule-of-thumb participants per predictor (non-binding)",
            [10, 15, 20, 25, 30],
            index=1,
            key="linreg_ppp"
        )
        st.caption("This is not a power calculation. It is a simple stability/sanity check.")
        st.write(f"Suggested N (rule-of-thumb) = {int(per_predictor) * int(n_predictors)}")

    if st.button("Calculate Sample Size", key="linreg_calc_btn"):
        if dropout_rate >= 0.95:
            st.error("Dropout rate too high. Please use < 0.95.")
            st.stop()

        # Note: two_sided is not used for regression F-test (always one-sided tail on F),
        # but we keep interface consistent and explicitly use alpha as-is.
        N0 = _n_for_multiple_regression_f2(alpha=alpha, power=power, f2=f2_plan, u=int(n_predictors))
        N_final = _adjust_for_dropout(N0, dropout_rate)

        # Intermediate values
        u = int(n_predictors)
        v0 = N0 - u - 1
        fcrit = stats.f.ppf(1 - alpha, u, v0)
        lam = f2_plan * N0
        power_now = 1.0 - stats.ncf.cdf(fcrit, u, v0, lam)

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"u (numerator df) = {u}")
        st.write(f"v (denominator df) = {v0}")
        st.write(f"F critical = {fcrit:.4f}")
        st.write(f"Noncentrality λ = {lam:.4f}")
        st.write(f"Achieved power (approx) = {power_now:.4f}")

        st.success(f"Required sample size (after dropout): {N_final}")
        st.write("Before dropout adjustment:", N0)

        paragraph = paragraph_linear_regression(
            alpha=alpha,
            power=power,
            f2=f2_plan,
            n_predictors=int(n_predictors),
            two_sided=two_sided,  # kept for template consistency
            dropout_rate=dropout_rate,
            n_required=N_final
        )

        st.markdown("### 📄 Methods Paragraph")
        st.code(paragraph)
# ==========================================
# ClinSample AI — Standardized Formula Edition
# ==========================================

import sys
import os

# Fix Streamlit Cloud import path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import streamlit as st

# Modular study pages
from app.study_pages.one_sample_mean_page import render as render_one_sample_mean
from app.study_pages.two_independent_means_page import render as render_two_independent_means
from app.study_pages.paired_mean_page import render as render_paired_mean
from app.study_pages.anova_oneway_page import render as render_anova_oneway
from app.study_pages.one_proportion_page import render as render_one_proportion
from app.study_pages.two_proportions_page import render as render_two_proportions   # ✅ NEW

# --------------------------------------------------
st.set_page_config(page_title="ClinSample AI", layout="centered")

st.title("ClinSample AI — Sample Size Calculator")
st.markdown("Mathematically standardized, thesis-ready sample size planning.")

# --------------------------------------------------
study_type = st.selectbox(
    "Select Study Type",
    [
        # Continuous
        "One-Sample Mean",
        "Two Independent Means",
        "Paired Mean",
        "One-Way ANOVA",

        # Binary
        "One Proportion",
        "Two Proportions",
        "Case-Control (Odds Ratio)",
        "Cohort (Risk Ratio)",

        # Association
        "Correlation",
        "Linear Regression",
        "Logistic Regression",

        # Survival
        "Survival (Log-Rank)"
    ]
)

# Sidebar
st.sidebar.header("Statistical Parameters")

alpha = st.sidebar.number_input("Alpha (Type I error)", 0.001, 0.2, 0.05, 0.001)
power = st.sidebar.number_input("Power (1 - Beta)", 0.5, 0.99, 0.8, 0.01)
dropout_rate = st.sidebar.number_input("Dropout Rate (0–1)", 0.0, 0.9, 0.0, 0.01)
two_sided = st.sidebar.checkbox("Two-sided test", True)

# ==========================================================
# ONE SAMPLE MEAN
# ==========================================================
if study_type == "One-Sample Mean":
    render_one_sample_mean(alpha, power, dropout_rate, two_sided)

# ==========================================================
# TWO INDEPENDENT MEANS
# ==========================================================
elif study_type == "Two Independent Means":
    render_two_independent_means(alpha, power, dropout_rate, two_sided)

# ==========================================================
# PAIRED MEAN
# ==========================================================
elif study_type == "Paired Mean":
    render_paired_mean(alpha, power, dropout_rate, two_sided)

# ==========================================================
# ONE-WAY ANOVA
# ==========================================================
elif study_type == "One-Way ANOVA":
    render_anova_oneway(alpha, power, dropout_rate, two_sided)

# ==========================================================
# ONE PROPORTION
# ==========================================================
elif study_type == "One Proportion":
    render_one_proportion(alpha, power, dropout_rate, two_sided)

# ==========================================================
# TWO PROPORTIONS  ✅ NEW
# ==========================================================
elif study_type == "Two Proportions":
    render_two_proportions(alpha, power, dropout_rate, two_sided)

# ==========================================================
# Remaining study types still inline (to be modularized)
# ==========================================================



# ==========================================================
# CASE–CONTROL (Odds Ratio)
# ==========================================================
elif study_type == "Case-Control (Odds Ratio)":

    import scipy.stats as stats
    import math

    st.header("Case–Control Study (Odds Ratio Based Sample Size)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used for unmatched case–control studies.

Examples:
• Association between smoking and lung cancer  
• Genetic variant and disease risk  
• Exposure vs outcome (retrospective design)

Design:
• Binary exposure
• Binary outcome
• Comparison based on Odds Ratio (OR)
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Log Odds Ratio Method)", expanded=True):

        st.latex(r"""
        p_1 = \frac{OR \cdot p_0}{1 - p_0 + OR \cdot p_0}
        """)

        st.latex(r"""
        n_1 =
        \frac{
        (Z_{\alpha} + Z_{\beta})^2
        \left(
        \frac{1}{p_0(1-p_0)} +
        \frac{1}{r \cdot p_1(1-p_1)}
        \right)
        }
        {(\ln OR)^2}
        """)

        st.latex(r"n_2 = r \cdot n_1")

        st.write("Where:")
        st.write("• p₀ = exposure prevalence in controls")
        st.write("• p₁ = exposure prevalence in cases (derived from OR)")
        st.write("• r = control-to-case ratio")
        st.write("• OR = target odds ratio")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance", expanded=False):

        st.markdown("""
**p₀ (Exposure prevalence in controls)**  
Sources:
• Registry data  
• Published literature  
• Pilot data  

**Odds Ratio (OR)**  
Should be:
• Clinically meaningful  
• Supported by literature  

Small OR (e.g., 1.2–1.5) → very large sample size  
Large OR (e.g., 2–3) → smaller sample size  

**Control-to-case ratio (r)**  
r = n_controls / n_cases  

• r = 1 → equal numbers  
• r > 1 → more controls (efficient when cases are rare)  
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    p0 = st.number_input(
        "Exposure Prevalence in Controls (p₀)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.30,
        key="cc_p0"
    )

    OR = st.number_input(
        "Target Odds Ratio (OR)",
        min_value=0.1,
        value=2.0,
        key="cc_or"
    )

    ratio = st.number_input(
        "Control-to-Case Ratio (r)",
        min_value=0.1,
        value=1.0,
        key="cc_ratio"
    )

    if st.button("Calculate Sample Size (Case-Control)", key="cc_calc"):

        # Derive p1
        p1 = (OR * p0) / (1 - p0 + OR * p0)

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        ln_or = math.log(OR)

        # Core formula
        numerator = (Z_alpha + Z_beta)**2 * (
            (1 / (p0*(1-p0))) +
            (1 / (ratio * p1*(1-p1)))
        )

        n1 = numerator / (ln_or**2)
        n2 = ratio * n1

        # Dropout adjustment
        n1_adj = math.ceil(n1 / (1 - dropout_rate))
        n2_adj = math.ceil(n2 / (1 - dropout_rate))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"Estimated p₁ (cases) = {round(p1,4)}")
        st.write(f"log(OR) = {round(ln_or,4)}")

        # Safe LaTeX block
        st.latex(rf"""
        n_1 =
        \frac{{
        ({round(Z_alpha,4)} + {round(Z_beta,4)})^2
        \left(
        \frac{{1}}{{{round(p0,4)}(1-{round(p0,4)})}} +
        \frac{{1}}{{{round(ratio,4)} \cdot {round(p1,4)}(1-{round(p1,4)})}}
        \right)
        }}
        {{({round(ln_or,4)})^2}}
        """)

        # --------------------------------------------------
        st.success(f"Required Cases (n₁): {n1_adj}")
        st.success(f"Required Controls (n₂): {n2_adj}")
        st.write(f"Total Sample Size: {n1_adj + n2_adj}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        st.code(f"""
Sample size was calculated for an unmatched case–control study using the log odds ratio method.
Assuming an exposure prevalence among controls of {p0},
a target odds ratio of {OR},
and a control-to-case ratio of {ratio},
the required sample size was {n1_adj} cases and {n2_adj} controls
(total {n1_adj + n2_adj}),
after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
        """)
# ==========================================================
# COHORT (Risk Ratio)
# ==========================================================
elif study_type == "Cohort (Risk Ratio)":

    import scipy.stats as stats
    import math

    st.header("Cohort Study (Risk Ratio Based Sample Size)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used for cohort studies or randomized trials
when comparing two independent proportions using Risk Ratio (RR).

Examples:
• Drug vs placebo event risk  
• Vaccinated vs unvaccinated infection risk  
• Exposed vs unexposed disease incidence  

Design:
• Binary outcome
• Independent groups
• Risk Ratio as primary effect measure
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Log Risk Ratio Method)", expanded=True):

        st.latex(r"""
        p_1 = RR \cdot p_0
        """)

        st.latex(r"""
        n_1 =
        \frac{
        (Z_{\alpha} + Z_{\beta})^2
        \left(
        \frac{1-p_0}{p_0} +
        \frac{1-p_1}{r \cdot p_1}
        \right)
        }
        {(\ln RR)^2}
        """)

        st.latex(r"n_2 = r \cdot n_1")

        st.write("Where:")
        st.write("• p₀ = baseline risk in control group")
        st.write("• p₁ = risk in exposed group")
        st.write("• RR = target risk ratio")
        st.write("• r = allocation ratio (n₂ / n₁)")

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance", expanded=False):

        st.markdown("""
**Baseline Risk (p₀)**  
Sources:
• Registry data  
• Prior cohort studies  
• RCT control arm  
• Pilot study  

**Risk Ratio (RR)**  
Should be:
• Clinically meaningful  
• Supported by literature  

RR close to 1 → very large sample size  
Large RR (e.g., 2–3) → smaller sample size  

**Allocation Ratio (r)**  
r = n₂ / n₁  

• r = 1 → equal groups  
• Unequal allocation increases total sample size
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    p0 = st.number_input(
        "Baseline Risk in Control Group (p₀)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        key="cohort_p0"
    )

    RR = st.number_input(
        "Target Risk Ratio (RR)",
        min_value=0.1,
        value=1.5,
        key="cohort_rr"
    )

    ratio = st.number_input(
        "Allocation Ratio (n₂ / n₁)",
        min_value=0.1,
        value=1.0,
        key="cohort_ratio"
    )

    if st.button("Calculate Sample Size (Cohort)", key="cohort_calc"):

        p1 = p0 * RR

        if p1 >= 1:
            st.error("RR too large for given baseline risk (p₁ ≥ 1).")
            st.stop()

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        ln_rr = math.log(RR)

        # Core formula
        numerator = (Z_alpha + Z_beta)**2 * (
            ((1 - p0) / p0) +
            ((1 - p1) / (ratio * p1))
        )

        n1 = numerator / (ln_rr**2)
        n2 = ratio * n1

        # Dropout adjustment
        n1_adj = math.ceil(n1 / (1 - dropout_rate))
        n2_adj = math.ceil(n2 / (1 - dropout_rate))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"Derived p₁ (exposed risk) = {round(p1,4)}")
        st.write(f"log(RR) = {round(ln_rr,4)}")

        # Safe LaTeX
        st.latex(rf"""
        n_1 =
        \frac{{
        ({round(Z_alpha,4)} + {round(Z_beta,4)})^2
        \left(
        \frac{{1-{round(p0,4)}}}{{{round(p0,4)}}} +
        \frac{{1-{round(p1,4)}}}{{{round(ratio,4)} \cdot {round(p1,4)}}}
        \right)
        }}
        {{({round(ln_rr,4)})^2}}
        """)

        # --------------------------------------------------
        st.success(f"Required Control Group (n₁): {n1_adj}")
        st.success(f"Required Exposed Group (n₂): {n2_adj}")
        st.write(f"Total Sample Size: {n1_adj + n2_adj}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        st.code(f"""
Sample size was calculated for a cohort study using the log risk ratio method.
Assuming a baseline risk of {p0} in the control group,
a target risk ratio of {RR},
and an allocation ratio of {ratio},
the required sample size was {n1_adj} participants in the control group
and {n2_adj} in the exposed group
(total {n1_adj + n2_adj}),
after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
        """)
# ==========================================================
# CORRELATION (Fisher z)
# ==========================================================
elif study_type == "Correlation":

    import scipy.stats as stats
    import math

    st.header("Correlation (Pearson r) — Sample Size via Fisher z-transform")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when your primary question is whether the **correlation** between two continuous variables
differs from 0 (or from a reference correlation).

Examples:
• Correlation between TyG index and HOMA-IR  
• Correlation between CRP and systolic blood pressure  
• Correlation between biomarker level and symptom score  

Assumptions (typical Pearson correlation planning):
• Independent observations  
• Approximately bivariate normality (or large enough sample for robustness)  
• Linear association is meaningful  
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Fisher z)", expanded=True):

        st.markdown("Fisher z-transform of correlation:")

        st.latex(r"""
        z = \frac{1}{2}\ln\left(\frac{1+r}{1-r}\right)
        """)

        st.markdown("Sample size formula (testing r against 0):")

        st.latex(r"""
        n =
        \frac{(Z_{\alpha} + Z_{\beta})^2}{z^2} + 3
        """)

        st.write("Where:")
        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)\ \text{(two-sided)}")
        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha)\ \text{(one-sided)}")
        st.latex(r"Z_{\beta} = \Phi^{-1}(\text{power})")
        st.latex(r"r = \text{target correlation (planning effect)}")

    # --------------------------------------------------
    with st.expander("📊 Choosing r (Effect Size) — Practical Guidance", expanded=False):
        st.markdown("""
**Target correlation (r)** is your expected or minimally meaningful correlation.

How to obtain r:
• From previous published studies reporting correlation  
• From pilot study correlation  
• From meta-analysis / systematic review  
• From domain knowledge (minimal meaningful association)

Interpretation heuristics (context-dependent):
• |r| ≈ 0.10 → small  
• |r| ≈ 0.30 → moderate  
• |r| ≈ 0.50 → large  

Notes:
• Smaller |r| → much larger n  
• Planning should use a **conservative (smaller)** |r| if unsure  
        """)

    # --------------------------------------------------
    with st.expander("🧮 Convert r ↔ Fisher z (for intuition)", expanded=False):

        r_demo = st.number_input(
            "Enter a correlation r to see Fisher z",
            min_value=-0.95,
            max_value=0.95,
            value=0.30,
            step=0.01,
            key="corr_demo_r"
        )

        z_demo = 0.5 * math.log((1 + r_demo) / (1 - r_demo))
        st.write(f"Fisher z = {round(z_demo,4)}")

        st.markdown("Inverse transform (z → r):")
        st.latex(r"""
        r = \frac{e^{2z}-1}{e^{2z}+1}
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    r_target = st.number_input(
        "Target Correlation (r)",
        min_value=-0.95,
        max_value=0.95,
        value=0.30,
        step=0.01,
        key="corr_r_target"
    )

    if st.button("Calculate Sample Size (Correlation)", key="corr_calc"):

        if abs(r_target) < 1e-6:
            st.error("r cannot be 0 for sample size planning. Choose a non-zero target correlation.")
            st.stop()

        if r_target <= -0.99 or r_target >= 0.99:
            st.error("r must be between -0.99 and 0.99.")
            st.stop()

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        # Fisher z
        z = 0.5 * math.log((1 + r_target) / (1 - r_target))

        # Sample size
        n_raw = ((Z_alpha + Z_beta) ** 2) / (z ** 2) + 3
        n = math.ceil(n_raw)

        # Dropout adjustment
        n_adj = math.ceil(n / (1 - dropout_rate))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"Fisher z = {round(z,4)}")
        st.write(f"n (before dropout) = {n}")

        st.latex(rf"""
        z = \frac{{1}}{{2}}\ln\left(\frac{{1+({round(r_target,4)})}}{{1-({round(r_target,4)})}}\right)
        """)

        st.latex(rf"""
        n =
        \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)})^2}}{{({round(z,4)})^2}} + 3
        """)

        st.success(f"Required Sample Size (adjusted): {n_adj}")
        st.write(f"Before Dropout Adjustment: {n}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        sided_txt = "two-sided" if two_sided else "one-sided"

        st.code(f"""
Sample size was calculated for detecting a Pearson correlation using Fisher’s z-transformation ({sided_txt}).
With α={alpha} and power={power}, and assuming a target correlation of r={r_target},
the required sample size was {n_adj} participants after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
        """)
# ==========================================================
# LINEAR REGRESSION (Cohen's f²)
# ==========================================================
elif study_type == "Linear Regression":

    import scipy.stats as stats
    import math

    st.header("Multiple Linear Regression — Sample Size via Cohen’s f²")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used when your primary analysis is **multiple linear regression** (continuous outcome)
and you want adequate power to detect an overall model effect or a set of predictors.

Examples:
• Predicting HbA1c from TyG, BMI, age, sex  
• Predicting blood pressure from waist circumference, smoking, lipids  
• Predicting depression score from biomarkers + covariates  

Typical assumptions:
• Independent observations  
• Linear relationship is a reasonable approximation  
• Residuals approximately normal (or sample sufficiently large)  
• Predictors not perfectly collinear  
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Formula (Cohen’s f²)", expanded=True):

        st.markdown("Cohen’s f² definition (from R²):")
        st.latex(r"""
        f^2 = \frac{R^2}{1 - R^2}
        """)

        st.markdown("Sample size planning (large-sample z-approximation):")
        st.latex(r"""
        n =
        \frac{(Z_{\alpha} + Z_{\beta})^2}{f^2} + p + 1
        """)

        st.write("Where:")
        st.write("• R² = expected proportion of variance explained by predictors")
        st.write("• f² = Cohen’s effect size for regression")
        st.write("• p = number of predictors (planned predictors in the model)")
        st.write("• Zα depends on one/two-sided α; Zβ depends on desired power")

        st.markdown("Optional: partial effect (incremental R²) for a block of predictors:")
        st.latex(r"""
        f^2_{\text{partial}} = \frac{\Delta R^2}{1 - R^2_{\text{full}}}
        """)

    # --------------------------------------------------
    with st.expander("🧮 Compute Cohen’s f² from R² (and from ΔR²)", expanded=False):

        st.markdown("""
Most users do not directly know f², but they often have an estimate of **R²** from literature or pilot models.

You can compute:
• **Overall f²** from overall R²  
• **Partial f²** from incremental ΔR² (e.g., effect of a predictor block)  
        """)

        tab1, tab2 = st.tabs(["Compute f² from R²", "Compute partial f² from ΔR²"])

        with tab1:
            r2 = st.number_input(
                "Overall R² (0–0.95 recommended)",
                min_value=0.0,
                max_value=0.99,
                value=0.20,
                step=0.01,
                key="linreg_r2_overall"
            )

            if st.button("Compute f² (overall)", key="linreg_calc_f2_overall"):
                if r2 >= 0.999:
                    st.error("R² is too close to 1. Use a realistic value (e.g., < 0.90).")
                else:
                    f2_overall = r2 / (1 - r2) if r2 < 1 else float("inf")
                    st.success(f"Cohen’s f² (overall) = {round(f2_overall,4)}")

                    st.markdown("Interpretation heuristics (context dependent):")
                    st.write("• f² ≈ 0.02 small")
                    st.write("• f² ≈ 0.15 medium")
                    st.write("• f² ≈ 0.35 large")

                    st.latex(rf"""
                    f^2 = \frac{{{round(r2,4)}}}{{1-{round(r2,4)}}}
                    """)

        with tab2:
            r2_full = st.number_input(
                "Full model R² (R²_full)",
                min_value=0.0,
                max_value=0.99,
                value=0.30,
                step=0.01,
                key="linreg_r2_full"
            )
            delta_r2 = st.number_input(
                "Incremental ΔR² (added block contribution)",
                min_value=0.0,
                max_value=0.50,
                value=0.05,
                step=0.01,
                key="linreg_delta_r2"
            )

            if st.button("Compute partial f²", key="linreg_calc_f2_partial"):
                if r2_full >= 0.999:
                    st.error("R²_full is too close to 1. Use a realistic value.")
                elif delta_r2 <= 0:
                    st.error("ΔR² must be > 0 to represent an added effect.")
                elif delta_r2 > r2_full:
                    st.error("ΔR² cannot exceed R²_full.")
                else:
                    f2_partial = delta_r2 / (1 - r2_full)
                    st.success(f"Partial Cohen’s f² = {round(f2_partial,4)}")

                    st.markdown("Interpretation heuristics (often used):")
                    st.write("• 0.02 small")
                    st.write("• 0.15 medium")
                    st.write("• 0.35 large")

                    st.latex(rf"""
                    f^2_{{partial}} = \frac{{{round(delta_r2,4)}}}{{1-{round(r2_full,4)}}}
                    """)

    # --------------------------------------------------
    with st.expander("📊 Parameter Guidance (Evidence-Based Choices)", expanded=False):
        st.markdown("""
**R² source hierarchy (best → acceptable):**
1) Pilot regression model on similar population  
2) Published regression model (same outcome + similar predictors)  
3) Meta-analysis / pooled models  
4) Conservative planning (smaller R² → larger sample)

**Predictor count (p):**
Include the predictors you plan to interpret or keep in the final model (not temporary screeners).

**Practical note:**
If you plan model selection / many candidate predictors, you often need more sample size than the basic formula suggests.
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning")

    f2 = st.number_input(
        "Cohen’s f² for Planning",
        min_value=0.0001,
        value=0.15,
        step=0.01,
        key="linreg_f2_plan"
    )

    p = st.number_input(
        "Number of Predictors (p)",
        min_value=1,
        value=5,
        step=1,
        key="linreg_p"
    )

    if st.button("Calculate Sample Size (Linear Regression)", key="linreg_calc_n"):

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        # Sample size formula
        n_raw = ((Z_alpha + Z_beta) ** 2) / f2 + p + 1
        n = math.ceil(n_raw)

        # Dropout adjustment
        n_adj = math.ceil(n / (1 - dropout_rate))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"f² = {round(f2,4)}")
        st.write(f"p = {int(p)}")
        st.write(f"n (before dropout) = {n}")

        st.latex(rf"""
        n =
        \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)})^2}}{{{round(f2,4)}}}
        + {int(p)} + 1
        """)

        st.success(f"Required Sample Size (adjusted): {n_adj}")
        st.write(f"Before Dropout Adjustment: {n}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        sided_txt = "two-sided" if two_sided else "one-sided"

        st.code(f"""
Sample size was calculated for multiple linear regression ({sided_txt}) using Cohen’s f² method.
With α={alpha} and power={power}, assuming an effect size of f²={f2} and {int(p)} predictors,
the required sample size was {n_adj} participants after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
        """)
# ==========================================================
# LOGISTIC REGRESSION (Full Upgrade: Meaning + Example + Derivation Tools)
# ==========================================================
elif study_type == "Logistic Regression":

    import scipy.stats as stats
    import math

    st.header("Logistic Regression — Power-Based Sample Size (Beyond EPV)")

    # --------------------------------------------------
    with st.expander("📘 What this calculator does (in plain language)", expanded=True):
        st.markdown("""
This module estimates the **minimum sample size** needed to detect an association in a logistic regression model,
using a **power-based Wald approximation**.

It is appropriate when:
• Outcome is **binary** (e.g., CKD yes/no, mortality yes/no)  
• You have an expected **effect size** (Odds Ratio) from pilot/literature  
• You know the **baseline probability** (event prevalence) of the outcome

This is a planning tool. Final modeling quality still depends on event count, predictor stability, and design.
        """)

    # --------------------------------------------------
    with st.expander("✅ Real Example (clinical)", expanded=True):
        st.markdown("""
**Example:** You want to study whether **high SII** is associated with **CKD (yes/no)**.

From literature/pilot:
• CKD prevalence in your target population is about **20%** → baseline event probability **p = 0.20**  
• You want to detect **OR = 1.50** for CKD per **1 SD increase** in SII (or per clinically defined exposure)  
• α = 0.05 (two-sided), power = 0.80, dropout 10%

This calculator returns the total sample size required.
Then we also check EPV (events per variable) for stability.
        """)

    # --------------------------------------------------
    with st.expander("📌 Meaning of key inputs", expanded=False):
        st.markdown("""
### 1) Baseline probability (event probability, p)
This is the expected probability that the **outcome = 1** in your target population.

Examples:
• CKD prevalence = 0.20 → p = 0.20  
• Mortality rate over follow-up = 0.08 → p = 0.08  
• Disease prevalence in a clinic = 0.35 → p = 0.35  

How to get p:
• Pilot study: events / total  
• Literature prevalence/incidence  
• Registry / hospital statistics

### 2) Target Odds Ratio (OR)
This is the effect size you want to detect.

Interpretation depends on predictor type:

**Binary predictor** (exposed vs unexposed):
• OR = 2.0 means exposed group has **2× higher odds** of outcome than unexposed.

**Continuous predictor** (per 1 unit):
• OR = 1.2 per 1-unit increase means each unit multiplies odds by 1.2.

**Per SD** reporting:
Some papers report OR per 1 SD increase. That is directly usable.

Important:
• OR close to 1.0 (e.g., 1.05–1.10) requires very large n.
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Foundation (Wald Approximation)", expanded=False):
        st.markdown("Logistic regression effect is expressed as a log-odds coefficient:")

        st.latex(r"""
        \beta = \ln(OR)
        """)

        st.markdown("Planning formula (power-based Wald approximation):")

        st.latex(r"""
        n =
        \frac{
        (Z_{\alpha} + Z_{\beta})^2
        }
        {
        p(1-p)\cdot (\ln(OR))^2
        }
        """)

        st.write("Where p is the overall event probability (outcome prevalence) used for planning.")

    # --------------------------------------------------
    with st.expander("🧮 Derive inputs from pilot / literature outputs", expanded=True):

        tabA, tabB, tabC = st.tabs([
            "A) p from pilot counts",
            "B) OR from two risks (p0, p1)",
            "C) Convert OR scale (per SD / per unit)"
        ])

        # -------------------------
        # A) p from pilot counts
        # -------------------------
        with tabA:
            st.markdown("If you have pilot counts, event probability is simply events / total.")
            events = st.number_input("Number of events (outcome=1)", min_value=0, value=20, step=1, key="logreg_events")
            total = st.number_input("Total sample size", min_value=1, value=100, step=1, key="logreg_total")

            if st.button("Compute p (event probability)", key="logreg_compute_p_from_counts"):
                p_from_counts = events / total
                st.success(f"Event probability p = {round(p_from_counts,4)}")

        # -------------------------
        # B) OR from two risks
        # -------------------------
        with tabB:
            st.markdown("""
If a paper reports event risks in two groups (e.g., exposed vs unexposed),
you can compute OR from p0 and p1:

OR = (p1/(1-p1)) / (p0/(1-p0))
            """)

            p0 = st.number_input("Risk in reference group (p₀)", min_value=0.0001, max_value=0.9999, value=0.20, key="logreg_p0_from_risks")
            p1 = st.number_input("Risk in exposed group (p₁)", min_value=0.0001, max_value=0.9999, value=0.30, key="logreg_p1_from_risks")

            if st.button("Compute OR from p₀ and p₁", key="logreg_compute_or_from_risks"):
                or_from_risks = (p1/(1-p1)) / (p0/(1-p0))
                st.success(f"Derived OR = {round(or_from_risks,4)}")

        # -------------------------
        # C) Convert OR scale
        # -------------------------
        with tabC:
            st.markdown("""
Sometimes papers report OR using different scaling:

**Case 1: OR per 1 SD increase**  
If you want OR per 1 unit, and SD is known:
OR_per_unit = exp( ln(OR_per_SD) / SD )

**Case 2: OR per IQR increase**  
If you want OR per 1 unit and IQR is known:
OR_per_unit = exp( ln(OR_per_IQR) / IQR )

This helps you harmonize effect sizes across studies.
            """)

            or_reported = st.number_input("Reported OR", min_value=0.01, value=1.50, key="logreg_or_reported")
            scale = st.selectbox("Reported OR is per:", ["1 SD", "IQR"], key="logreg_scale_type")
            scale_value = st.number_input("SD or IQR value", min_value=0.0001, value=10.0, key="logreg_scale_value")

            if st.button("Convert to OR per 1 unit", key="logreg_convert_or"):
                ln_or = math.log(or_reported)
                ln_or_per_unit = ln_or / scale_value
                or_per_unit = math.exp(ln_or_per_unit)
                st.success(f"OR per 1 unit ≈ {round(or_per_unit,4)}")

    # --------------------------------------------------
    with st.expander("⚠ Important practical note (what this formula does NOT include)", expanded=False):
        st.markdown("""
This power-based Wald formula is a **planning approximation**.
It does not fully account for:
• multiple predictors correlation (multicollinearity)  
• nonlinearity / splines / interactions  
• model selection or high-dimensional screening  
• rare events correction / penalized regression  

That’s why we also provide an EPV stability check.
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Planning (use your best p and OR)")

    p_event = st.number_input(
        "Event Probability p (Outcome prevalence)",
        min_value=0.0001,
        max_value=0.9999,
        value=0.20,
        key="logreg_p_event_plan"
    )

    OR = st.number_input(
        "Target Odds Ratio (OR)",
        min_value=0.01,
        value=1.50,
        key="logreg_or_plan"
    )

    n_predictors = st.number_input(
        "Number of Predictors in Final Model",
        min_value=1,
        value=5,
        step=1,
        key="logreg_predictors_plan"
    )

    epv_target = st.number_input(
        "EPV threshold for stability (common defaults 10–20)",
        min_value=5,
        value=10,
        step=1,
        key="logreg_epv_target"
    )

    if st.button("Calculate Sample Size (Logistic Regression)", key="logreg_calc_final"):

        # Z values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        ln_or = math.log(OR)

        if abs(ln_or) < 1e-12:
            st.error("OR cannot be 1 (no effect). Choose an OR different from 1.")
            st.stop()

        p_term = p_event * (1 - p_event)

        if p_term <= 0:
            st.error("p must be strictly between 0 and 1.")
            st.stop()

        # Wald planning formula
        n_raw = ((Z_alpha + Z_beta) ** 2) / (p_term * (ln_or ** 2))
        n_before_dropout = math.ceil(n_raw)
        n_adj = math.ceil(n_before_dropout / (1 - dropout_rate))

        # EPV check
        required_events = epv_target * int(n_predictors)
        expected_events = n_adj * p_event

        st.markdown("### 🔎 Intermediate Values")
        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"ln(OR) = {round(ln_or,4)}")
        st.write(f"p(1-p) = {round(p_term,4)}")

        st.latex(rf"""
        n =
        \frac{{({round(Z_alpha,4)} + {round(Z_beta,4)})^2}}
        {{{round(p_term,4)}\cdot ({round(ln_or,4)})^2}}
        """)

        st.success(f"Required Sample Size (adjusted): {n_adj}")
        st.write(f"Before Dropout Adjustment: {n_before_dropout}")

        st.markdown("### 🔎 EPV Stability Check")
        st.write(f"Planned predictors: {int(n_predictors)}")
        st.write(f"EPV target: {int(epv_target)}")
        st.write(f"Required events = EPV × predictors = {required_events}")
        st.write(f"Expected events = n × p = {round(expected_events,1)}")

        if expected_events < required_events:
            st.warning(
                "⚠ EPV stability criterion NOT met. "
                "Consider increasing sample size, reducing predictors, or using penalized regression."
            )
        else:
            st.success("✔ EPV stability criterion met.")

        st.markdown("### 📄 Copy for Thesis / Manuscript")
        sided_txt = "two-sided" if two_sided else "one-sided"

        st.code(f"""
Sample size for logistic regression ({sided_txt}) was planned using a power-based Wald approximation.
With α={alpha} and power={power}, assuming an outcome event probability of p={p_event}
and a target odds ratio of OR={OR} (β=ln(OR)),
the required sample size was {n_adj} participants after adjusting for {dropout_rate*100:.1f}% anticipated dropout.
Model stability was additionally assessed using an EPV threshold of {epv_target} with {int(n_predictors)} predictors.
        """)
# ==========================================================
# SURVIVAL (LOG-RANK) — Full Professional Version
# ==========================================================
elif study_type == "Survival (Log-Rank)":

    import scipy.stats as stats
    import math

    st.header("Survival Analysis — Log-Rank Test Sample Size (Event-Driven)")

    # --------------------------------------------------
    with st.expander("📘 When to Use This Design", expanded=True):
        st.markdown("""
Used for comparing time-to-event outcomes between two independent groups.

Examples:
• Overall survival in oncology trials  
• Time to relapse  
• Time to cardiovascular event  
• Device failure time  

Key principle:
Log-rank tests are **event-driven**, meaning required sample size
depends primarily on the number of events, not just participants.
        """)

    # --------------------------------------------------
    with st.expander("📐 Mathematical Foundation (Schoenfeld Method)", expanded=True):

        st.markdown("### Required Number of Events")

        st.latex(
            r"D = \frac{(Z_{\alpha} + Z_{\beta})^2}{(\ln(HR))^2 \cdot p(1-p)}"
        )

        st.markdown("Where:")

        st.latex(r"HR = \text{Hazard Ratio}")
        st.latex(r"p = \text{Allocation proportion in group 1}")
        st.latex(r"Z_{\alpha} = \Phi^{-1}(1-\alpha/2)")
        st.latex(r"Z_{\beta} = \Phi^{-1}(power)")

        st.markdown("### Total Sample Size Approximation")

        st.latex(
            r"N = \frac{D}{\text{Expected Event Rate}}"
        )

    # --------------------------------------------------
    with st.expander("📊 Parameter Interpretation", expanded=False):
        st.markdown("""
**Hazard Ratio (HR)**  
HR < 1 → protective effect  
HR > 1 → harmful effect  

Example:
HR = 0.70 means 30% reduction in hazard.

---

**Allocation Proportion (p)**  
If equal randomization → p = 0.5  
If 2:1 design → p = 0.67  

---

**Expected Event Rate**  
Proportion of participants expected to experience the event
during follow-up.

Sources:
• Previous trials  
• Registry data  
• Meta-analysis  
• Pilot survival curve  

Lower event rate → larger required N.
        """)

    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Survival Sample Size Calculation")

    hr = st.number_input(
        "Target Hazard Ratio (HR)",
        min_value=0.01,
        value=0.70,
        key="surv_hr"
    )

    alloc_ratio = st.number_input(
        "Allocation Ratio (n₂ / n₁)",
        min_value=0.1,
        value=1.0,
        key="surv_ratio"
    )

    event_rate = st.number_input(
        "Expected Overall Event Rate (0–1)",
        min_value=0.01,
        max_value=0.99,
        value=0.50,
        key="surv_event_rate"
    )

    if st.button("Calculate Survival Sample Size", key="surv_calc"):

        # Z-values
        if two_sided:
            Z_alpha = stats.norm.ppf(1 - alpha/2)
        else:
            Z_alpha = stats.norm.ppf(1 - alpha)

        Z_beta = stats.norm.ppf(power)

        ln_hr = math.log(hr)

        # allocation proportion p
        p = 1 / (1 + alloc_ratio)

        # required events
        D = ((Z_alpha + Z_beta)**2) / ((ln_hr**2) * p * (1 - p))

        # total sample size approximation
        N_total = D / event_rate

        N_total_adj = math.ceil(N_total / (1 - dropout_rate))

        n1 = math.ceil(N_total_adj * p)
        n2 = math.ceil(N_total_adj * (1 - p))

        # --------------------------------------------------
        st.markdown("### 🔎 Intermediate Values")

        st.write(f"Zα = {round(Z_alpha,4)}")
        st.write(f"Zβ = {round(Z_beta,4)}")
        st.write(f"log(HR) = {round(ln_hr,4)}")
        st.write(f"Allocation proportion p = {round(p,4)}")
        st.write(f"Required Events (D) = {math.ceil(D)}")

        st.latex(
            rf"D = \frac{{({round(Z_alpha,3)} + {round(Z_beta,3)})^2}}{{({round(ln_hr,3)})^2 \cdot {round(p,3)}(1-{round(p,3)})}}"
        )

        st.success(f"Total Required Sample Size: {N_total_adj}")
        st.success(f"Group 1 (n₁): {n1}")
        st.success(f"Group 2 (n₂): {n2}")

        # --------------------------------------------------
        st.markdown("### 📄 Copy for Thesis / Manuscript")

        st.code(f"""
Sample size was calculated for a survival analysis using the log-rank test
based on Schoenfeld’s method.

Assuming:
• Two-sided α = {alpha}
• Power = {power}
• Target hazard ratio = {hr}
• Expected event rate = {event_rate}
• Allocation ratio (n2/n1) = {alloc_ratio}

The required number of events was {math.ceil(D)},
resulting in a total sample size of {N_total_adj} participants
(after adjusting for {dropout_rate*100:.1f}% anticipated dropout),
with {n1} participants in group 1 and {n2} in group 2.
        """)

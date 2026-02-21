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
from app.study_pages.two_proportions_page import render as render_two_proportions
from app.study_pages.case_control_or_page import render as render_case_control_or
from app.study_pages.cohort_rr_page import render as render_cohort_rr 
from app.study_pages.correlation_page import render as render_correlation
from app.study_pages.linear_regression_page import render as render_linear_regression 
from app.study_pages.logistic_regression_page import render as render_logistic_regression  # ✅ NEW

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
# CASE-CONTROL (ODDS RATIO)  ✅ NEW
# ==========================================================
elif study_type == "Case-Control (Odds Ratio)":
    render_case_control_or(alpha, power, dropout_rate, two_sided)

# ==========================================================
# COHORT (RISK RATIO) ✅ NEW
# ==========================================================
elif study_type == "Cohort (Risk Ratio)":

    render_cohort_rr(alpha, power, dropout_rate, two_sided)
# ==========================================================
# CORRELATION ✅ NEW
# ==========================================================
elif study_type == "Correlation":

    render_correlation(alpha, power, dropout_rate, two_sided)

# ==========================================================
# LINEAR REGRESSION ✅ NEW
# ==========================================================
elif study_type == "Linear Regression":

    render_linear_regression(alpha, power, dropout_rate, two_sided)
# ==========================================================
# LOGISTIC REGRESSION ✅ NEW
# ==========================================================
elif study_type == "Logistic Regression":

    render_logistic_regression(alpha, power, dropout_rate, two_sided)
# ==========================================================
# Remaining study types still inline (to be modularized)
# ==========================================================


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

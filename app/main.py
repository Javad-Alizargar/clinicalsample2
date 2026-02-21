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
from app.study_pages.logistic_regression_page import render as render_logistic_regression
from app.study_pages.logrank_page import render as render_logrank
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
# SURVIVAL (LOG-RANK) ✅ NEW
# ==========================================================
elif study_type == "Survival (Log-Rank)":

    render_logrank(alpha, power, dropout_rate, two_sided)
# ==========================================================
# Remaining study types still inline (to be modularized)
# ==========================================================

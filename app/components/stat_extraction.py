
# ==========================================
# Statistical Extraction Utilities Component
# ==========================================

import streamlit as st
import math


def render_sd_extraction_section(prefix="sd_extract"):

    with st.expander("🧠 Extract SD from Common Abstract Statistics", expanded=False):

        tab1, tab2, tab3 = st.tabs([
            "SD from 95% CI",
            "SD from SE",
            "SD from IQR"
        ])

        # ---- SD from CI ----
        with tab1:

            lower = st.number_input(
                "CI lower",
                value=95.0,
                key=f"{prefix}_ci_lower"
            )

            upper = st.number_input(
                "CI upper",
                value=105.0,
                key=f"{prefix}_ci_upper"
            )

            n_ci = st.number_input(
                "Sample size (n)",
                min_value=2,
                value=50,
                key=f"{prefix}_ci_n"
            )

            if st.button("Compute SD from CI", key=f"{prefix}_ci_btn"):
                Z = 1.96
                se = (upper - lower) / (2 * Z)
                sd = se * math.sqrt(n_ci)
                st.success(f"Estimated SD ≈ {round(sd,4)}")

        # ---- SD from SE ----
        with tab2:

            se_val = st.number_input(
                "Standard Error (SE)",
                value=2.0,
                key=f"{prefix}_se_val"
            )

            n_se = st.number_input(
                "Sample size (n)",
                min_value=2,
                value=50,
                key=f"{prefix}_se_n"
            )

            if st.button("Compute SD from SE", key=f"{prefix}_se_btn"):
                sd = se_val * math.sqrt(n_se)
                st.success(f"Estimated SD ≈ {round(sd,4)}")

        # ---- SD from IQR ----
        with tab3:

            iqr = st.number_input(
                "IQR (Q3 − Q1)",
                value=10.0,
                key=f"{prefix}_iqr_val"
            )

            if st.button("Approximate SD from IQR", key=f"{prefix}_iqr_btn"):
                sd = iqr / 1.35
                st.success(f"Approximate SD ≈ {round(sd,4)}")

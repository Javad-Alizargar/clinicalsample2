# ==========================================
# Two Proportions — Modular Advanced Version (Option B)
# ==========================================

import math
import streamlit as st
import scipy.stats as stats

from calculators.binary.two_proportions import calculate_two_proportions
from templates.paragraph_templates import paragraph_two_proportions

from app.components.pubmed_section import render_pubmed_section


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default


def _p_from_counts(events: float, total: float):
    if total <= 0:
        return None
    return _clamp01(events / total)


def _se_from_ci_prop(p_hat: float, ci_low: float, ci_high: float, alpha: float = 0.05):
    """
    Approx SE from a symmetric Wald-style CI width: p ± Z * SE
    SE ≈ (upper - lower) / (2*Z)
    """
    z = stats.norm.ppf(1 - alpha / 2)
    width = (ci_high - ci_low)
    if z <= 0 or width <= 0:
        return None
    return width / (2 * z)


def _n_from_wald_ci(p_hat: float, se: float):
    """
    For proportion: SE ≈ sqrt(p(1-p)/n) => n ≈ p(1-p)/SE^2
    """
    if se is None or se <= 0:
        return None
    denom = se ** 2
    n = (p_hat * (1 - p_hat)) / denom
    if n <= 0:
        return None
    return n


def _p2_from_rr(p1: float, rr: float):
    return _clamp01(p1 * rr)


def _p2_from_or(p1: float, odds_ratio: float):
    """
    If OR = (p2/(1-p2)) / (p1/(1-p1))
    => p2 = OR*p1 / (1 - p1 + OR*p1)
    """
    p1 = _clamp01(p1)
    orr = float(odds_ratio)
    denom = (1 - p1) + (orr * p1)
    if denom <= 0:
        return None
    return _clamp01((orr * p1) / denom)


def _p2_from_arr(p1: float, arr: float, direction: str):
    """
    ARR = |p2 - p1|. direction decides whether p2 > p1 or p2 < p1.
    """
    p1 = _clamp01(p1)
    arr = abs(float(arr))
    if direction == "Increase":
        return _clamp01(p1 + arr)
    return _clamp01(p1 - arr)


def _p2_from_rrr(p1: float, rrr: float, direction: str):
    """
    RRR usually refers to reduction from baseline risk: p2 = p1*(1-rrr)
    If direction is Increase, we treat it as increase: p2 = p1*(1+rrr)
    """
    p1 = _clamp01(p1)
    rrr = abs(float(rrr))
    if direction == "Increase":
        return _clamp01(p1 * (1 + rrr))
    return _clamp01(p1 * (1 - rrr))


def render(alpha: float, power: float, dropout_rate: float, two_sided: bool):
    st.header("Two Proportions — Sample Size Planning (Advanced)")

    # ----------------------------------------------------------
    # Concept
    # ----------------------------------------------------------
    with st.expander("📘 Study Design Explanation", expanded=True):
        st.markdown(
            """
Use when comparing a **binary outcome** between **two independent groups**.

Examples:
- Event rate: infection (yes/no) in Treatment vs Control
- Response rate: remission vs no remission in Drug A vs Drug B
- Complication rate: bleeding vs none in Procedure 1 vs Procedure 2

Inputs required:
- **p1**: expected proportion in group 1
- **p2**: expected proportion in group 2
- **Allocation ratio** *(r = n2/n1)*

Where to get p1/p2:
- Prior trials, pilot study, registry studies
- Meta-analyses
- Sometimes abstracts report event counts or percentages directly
            """
        )

    # ----------------------------------------------------------
    # Formula
    # ----------------------------------------------------------
    with st.expander("📐 Mathematical Formula (Z-test, pooled variance)", expanded=True):
        st.latex(r"r = \frac{n_2}{n_1}")
        st.latex(r"\Delta = |p_1 - p_2|")
        st.latex(r"\bar{p} = \frac{p_1 + r p_2}{1+r}")
        st.latex(r"\mathrm{Var}_{H_0} = \bar{p}(1-\bar{p})\left(1+\frac{1}{r}\right)")
        st.latex(r"\mathrm{Var}_{H_1} = p_1(1-p_1)+\frac{p_2(1-p_2)}{r}")
        st.latex(
            r"""
n_1 =
\frac{\left(Z_\alpha\sqrt{\mathrm{Var}_{H_0}} + Z_\beta\sqrt{\mathrm{Var}_{H_1}}\right)^2}{\Delta^2},
\quad
n_2 = r n_1
            """
        )
        st.caption("Your calculator implements this pooled-variance approach with dropout adjustment.")

    # ----------------------------------------------------------
    # Extract p1/p2 helper (from abstract-friendly stats)
    # ----------------------------------------------------------
    st.subheader("🧠 Extract p1 / p2 from Common Abstract Statistics")

    tab_counts, tab_percent, tab_rr_or, tab_arr_rrr, tab_ci = st.tabs(
        [
            "A) From counts",
            "B) From % + n",
            "C) From RR / OR + baseline",
            "D) From ARR / RRR + baseline",
            "E) From 95% CI (approx)"
        ]
    )

    # Store suggested values in session state so user can transfer
    if "two_prop_suggest_p1" not in st.session_state:
        st.session_state["two_prop_suggest_p1"] = None
    if "two_prop_suggest_p2" not in st.session_state:
        st.session_state["two_prop_suggest_p2"] = None

    with tab_counts:
        st.markdown("If an abstract reports event counts like **12/80 vs 25/78**, compute proportions directly.")
        c1 = st.number_input("Group 1 events", min_value=0, value=12, step=1, key="tp_c_ev1")
        n1 = st.number_input("Group 1 total (n1)", min_value=1, value=80, step=1, key="tp_c_n1")
        c2 = st.number_input("Group 2 events", min_value=0, value=25, step=1, key="tp_c_ev2")
        n2 = st.number_input("Group 2 total (n2)", min_value=1, value=78, step=1, key="tp_c_n2")

        if st.button("Compute p1 & p2", key="tp_c_btn"):
            p1 = _p_from_counts(c1, n1)
            p2 = _p_from_counts(c2, n2)
            st.session_state["two_prop_suggest_p1"] = p1
            st.session_state["two_prop_suggest_p2"] = p2
            st.success(f"p1 = {p1:.4f}   |   p2 = {p2:.4f}")
            st.caption("You can copy these into the planning section below.")

    with tab_percent:
        st.markdown("If an abstract reports **percent (%)** and sample size **n**, compute p = %/100.")
        p1_pct = st.number_input("Group 1 %", min_value=0.0, max_value=100.0, value=15.0, step=0.1, key="tp_pct_p1")
        p2_pct = st.number_input("Group 2 %", min_value=0.0, max_value=100.0, value=32.1, step=0.1, key="tp_pct_p2")

        if st.button("Convert % to proportions", key="tp_pct_btn"):
            p1 = _clamp01(p1_pct / 100.0)
            p2 = _clamp01(p2_pct / 100.0)
            st.session_state["two_prop_suggest_p1"] = p1
            st.session_state["two_prop_suggest_p2"] = p2
            st.success(f"p1 = {p1:.4f}   |   p2 = {p2:.4f}")

    with tab_rr_or:
        st.markdown(
            """
Many abstracts report **RR** or **OR** relative to a baseline risk.
If you know **baseline p1**, derive **p2**.

- RR: p2 = p1 × RR  
- OR: p2 = OR·p1 / (1 − p1 + OR·p1)
            """
        )
        baseline = st.number_input("Baseline risk p1", min_value=0.0001, max_value=0.9999, value=0.20, step=0.01, key="tp_rr_base")
        metric = st.selectbox("Metric type", ["Risk Ratio (RR)", "Odds Ratio (OR)"], key="tp_rr_metric")
        val = st.number_input("RR or OR value", min_value=0.0001, value=0.70, step=0.01, key="tp_rr_val")

        if st.button("Derive p2", key="tp_rr_btn"):
            p1 = _clamp01(baseline)
            if metric.startswith("Risk"):
                p2 = _p2_from_rr(p1, val)
            else:
                p2 = _p2_from_or(p1, val)

            st.session_state["two_prop_suggest_p1"] = p1
            st.session_state["two_prop_suggest_p2"] = p2
            st.success(f"Derived: p1 = {p1:.4f}   |   p2 = {p2:.4f}")
            st.caption("Check plausibility: derived p2 should be clinically reasonable and within [0,1].")

    with tab_arr_rrr:
        st.markdown(
            """
If you know baseline risk **p1** and an absolute or relative change:

- ARR (absolute risk reduction): p2 = p1 − ARR (or + ARR if increase)
- RRR (relative risk reduction): p2 = p1 × (1 − RRR) (or ×(1+RRR) if increase)

Choose direction carefully.
            """
        )
        baseline2 = st.number_input("Baseline risk p1", min_value=0.0001, max_value=0.9999, value=0.30, step=0.01, key="tp_arr_base")
        kind = st.selectbox("Effect type", ["ARR (absolute)", "RRR (relative)"], key="tp_arr_kind")
        direction = st.selectbox("Direction", ["Decrease", "Increase"], key="tp_arr_dir")
        eff = st.number_input("ARR or RRR", min_value=0.0, value=0.05, step=0.01, key="tp_arr_eff")

        if st.button("Derive p2 from ARR/RRR", key="tp_arr_btn"):
            p1 = _clamp01(baseline2)
            if kind.startswith("ARR"):
                p2 = _p2_from_arr(p1, eff, direction)
            else:
                p2 = _p2_from_rrr(p1, eff, direction)

            st.session_state["two_prop_suggest_p1"] = p1
            st.session_state["two_prop_suggest_p2"] = p2
            st.success(f"Derived: p1 = {p1:.4f}   |   p2 = {p2:.4f}")

    with tab_ci:
        st.markdown(
            """
Sometimes an abstract reports **p with a 95% CI** but not n.
You can approximate **SE** from CI width and back-calculate an implied n (Wald approximation).

This is **rough** (depends on CI method), but can help when no other info is available.
            """
        )
        p_hat = st.number_input("Reported proportion p̂", min_value=0.0001, max_value=0.9999, value=0.20, step=0.01, key="tp_ci_phat")
        lo = st.number_input("95% CI lower", min_value=0.0, max_value=1.0, value=0.15, step=0.01, key="tp_ci_lo")
        hi = st.number_input("95% CI upper", min_value=0.0, max_value=1.0, value=0.26, step=0.01, key="tp_ci_hi")

        if st.button("Estimate SE and implied n", key="tp_ci_btn"):
            se = _se_from_ci_prop(p_hat, lo, hi, alpha=0.05)
            n_imp = _n_from_wald_ci(p_hat, se) if se else None
            if se is None or n_imp is None:
                st.error("Could not estimate from inputs. Check CI ordering and values.")
            else:
                st.success(f"Estimated SE ≈ {se:.6f}")
                st.success(f"Implied n ≈ {n_imp:.1f}")
                st.caption("Use implied n only as a sanity check; prefer real n from the paper when possible.")

    # ----------------------------------------------------------
    # PubMed helper
    # ----------------------------------------------------------
    render_pubmed_section(
        study_type="Two Proportions",
        default_outcome="response rate",
        default_population="randomized trial",
        default_extra="event rate OR proportion OR risk ratio OR odds ratio",
        key_prefix="two_prop_pubmed",
        expanded=False
    )

    # ----------------------------------------------------------
    # Final calculation
    # ----------------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Final Sample Size Calculation")

    # Suggestion box (if available)
    sug_p1 = st.session_state.get("two_prop_suggest_p1", None)
    sug_p2 = st.session_state.get("two_prop_suggest_p2", None)
    if sug_p1 is not None or sug_p2 is not None:
        st.info(
            f"Suggested from helper: "
            f"p1={('%.4f' % sug_p1) if sug_p1 is not None else '—'} , "
            f"p2={('%.4f' % sug_p2) if sug_p2 is not None else '—'}"
        )

    p1 = st.number_input(
        "Proportion in Group 1 (p1)",
        min_value=0.0001,
        max_value=0.9999,
        value=float(sug_p1) if sug_p1 is not None else 0.20,
        step=0.01,
        key="two_prop_final_p1"
    )

    p2 = st.number_input(
        "Proportion in Group 2 (p2)",
        min_value=0.0001,
        max_value=0.9999,
        value=float(sug_p2) if sug_p2 is not None else 0.14,
        step=0.01,
        key="two_prop_final_p2"
    )

    allocation_ratio = st.number_input(
        "Allocation ratio (n2 / n1)",
        min_value=0.1,
        value=1.0,
        step=0.1,
        key="two_prop_final_ratio"
    )

    if st.button("Calculate Sample Size", key="two_prop_calc_btn"):
        if dropout_rate >= 0.95:
            st.error("Dropout rate too high. Please use < 0.95.")
            st.stop()

        try:
            result = calculate_two_proportions(
                alpha=alpha,
                power=power,
                p1=p1,
                p2=p2,
                allocation_ratio=allocation_ratio,
                two_sided=two_sided,
                dropout_rate=dropout_rate
            )

            Z_alpha = stats.norm.ppf(1 - alpha / 2) if two_sided else stats.norm.ppf(1 - alpha)
            Z_beta = stats.norm.ppf(power)

            st.markdown("### 🔎 Intermediate Values")
            st.write(f"Zα = {Z_alpha:.4f}")
            st.write(f"Zβ = {Z_beta:.4f}")
            st.write(f"Δ = |p1 − p2| = {abs(p1 - p2):.4f}")

            st.success(f"Group 1 Required: {result['n_group1']}")
            st.success(f"Group 2 Required: {result['n_group2']}")
            st.write("Total Sample Size:", result["n_total"])
            st.write("Before dropout adjustment:", f"n1={result['n1_before_dropout']}, n2={result['n2_before_dropout']}")

            st.markdown("### 📄 Methods Paragraph")
            paragraph = paragraph_two_proportions(
                alpha=alpha,
                power=power,
                p1=p1,
                p2=p2,
                allocation_ratio=allocation_ratio,
                two_sided=two_sided,
                dropout_rate=dropout_rate,
                n1=result["n_group1"],
                n2=result["n_group2"],
            )
            st.code(paragraph)

            with st.expander("Assumptions (for reporting)", expanded=False):
                for a in result.get("assumptions", []):
                    st.write(f"• {a}")

        except Exception as e:
            st.error(f"Calculation failed: {e}")
"""
Three-Level CRT Calculator page (CRA3_3 and BCRA3_2).

CRA3_3:  Top-level units (e.g., districts) are randomly assigned.
BCRA3_2: Level-2 units (e.g., schools) are randomly assigned within
         level-3 blocks (e.g., districts).
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from mdes_engines import compute_mdes_bcra3_2, compute_mdes_cra3_3
from mdes_engines.mdes_two_level import MDESResult

st.set_page_config(
    page_title="Three-Level CRT – MDES Calculator",
    page_icon="🏙️",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏙️ Three-Level Cluster Randomized Trial")
st.write(
    "Use this page when you have a three-level nesting structure "
    "(e.g., students within schools within districts).  Choose between "
    "randomizing at the top level or within blocks."
)

# ── Design selector ───────────────────────────────────────────────────────────
design_choice = st.radio(
    "Select the three-level design variant:",
    options=[
        "CRA3_3 – Districts (or top-level orgs) randomized",
        "BCRA3_2 – Schools randomized within districts (districts as blocks)",
    ],
    index=0
    if st.session_state.get("selected_design", "CRA3_3") != "BCRA3_2"
    else 1,
    horizontal=True,
)
is_cra3_3 = design_choice.startswith("CRA3_3")

with st.expander("📖 Statistical background"):
    if is_cra3_3:
        st.markdown(
            r"""
**CRA3_3 formula** (Dong & Maynard, 2013):

$$
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho_3\,(1 - R^2_3)}{P(1-P)\,K}
    +\frac{\rho_2\,(1 - R^2_2)}{P(1-P)\,K\,J}
    +\frac{(1-\rho_3-\rho_2)\,(1 - R^2_1)}{P(1-P)\,K\,J\,n}
}
$$

$\nu = K - 2$, where $K$ = level-3 units, $J$ = level-2 units per level-3, $n$ = level-1 per level-2.
"""
        )
    else:
        st.markdown(
            r"""
**BCRA3_2 formula** (Dong & Maynard, 2013):

Level-3 variance is absorbed by blocking (fixed level-3 effects):

$$
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho_2\,(1 - R^2_2)}{P(1-P)\,K\,J}
    +\frac{(1-\rho_3-\rho_2)\,(1 - R^2_1)}{P(1-P)\,K\,J\,n}
}
$$

$\nu = K\,(J - 2)$, where $K$ = blocks (districts), $J$ = schools per district, $n$ = students per school.
"""
        )

st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
st.header("⚙️ Study parameters")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Sample size")
    if is_cra3_3:
        n_level3 = st.number_input(
            "Number of level-3 units / districts (K)",
            min_value=3,
            max_value=1_000,
            value=20,
            step=1,
            help="Total number of top-level units (e.g., districts, health systems).",
        )
    else:
        n_level3 = st.number_input(
            "Number of blocks / districts (K)",
            min_value=1,
            max_value=1_000,
            value=10,
            step=1,
            help="Number of level-3 blocks (e.g., districts) within which randomization occurs.",
        )
    n_level2 = st.number_input(
        "Level-2 units per level-3 unit / block (J)",
        min_value=3 if not is_cra3_3 else 1,
        max_value=1_000,
        value=5,
        step=1,
        help="Number of schools (or similar units) per district.",
    )
    cluster_size = st.number_input(
        "Individuals per level-2 unit (n)",
        min_value=1,
        max_value=10_000,
        value=25,
        step=1,
        help="Average number of students (or participants) per school.",
    )
    p_treat = st.slider(
        "Proportion assigned to treatment (P)",
        min_value=0.1,
        max_value=0.9,
        value=0.5,
        step=0.05,
    )

with col_right:
    st.subheader("ICCs & covariates")
    icc3 = st.slider(
        "ICC at level 3 (ρ₃)",
        min_value=0.00,
        max_value=0.50,
        value=0.05,
        step=0.01,
        format="%.2f",
        help="Proportion of variance between level-3 units.",
    )
    icc2 = st.slider(
        "ICC at level 2 (ρ₂)",
        min_value=0.00,
        max_value=0.50,
        value=0.10,
        step=0.01,
        format="%.2f",
        help="Proportion of variance between level-2 units (net of level-3).",
    )
    if icc2 + icc3 >= 1.0:
        st.error("ρ₂ + ρ₃ must be < 1.  Please reduce one of the ICCs.")

    r2_level1 = st.slider("Individual-level R² (R²₁)", 0.00, 0.99, 0.00, 0.01, format="%.2f")
    r2_level2 = st.slider("Level-2 covariate R² (R²₂)", 0.00, 0.99, 0.00, 0.01, format="%.2f")
    if is_cra3_3:
        r2_level3 = st.slider(
            "Level-3 covariate R² (R²₃)", 0.00, 0.99, 0.00, 0.01, format="%.2f"
        )
    else:
        r2_level3 = 0.0

st.subheader("Statistical test settings")
col_a, col_b = st.columns(2)
with col_a:
    alpha = st.selectbox("Significance level (α)", [0.01, 0.05, 0.10], index=1, format_func=lambda x: f"{x:.2f}")
with col_b:
    power = st.selectbox("Statistical power (1 − β)", [0.70, 0.75, 0.80, 0.85, 0.90], index=2, format_func=lambda x: f"{x:.0%}")

st.subheader("Outcome type")
outcome_type = st.radio("Outcome type", ["continuous", "binary"], horizontal=True, label_visibility="collapsed")
baseline_prob: Optional[float] = None
outcome_sd: Optional[float] = None
if outcome_type == "binary":
    baseline_prob = st.slider("Baseline event probability (p₀)", 0.01, 0.99, 0.30, 0.01, format="%.2f")
else:
    sd_input = st.number_input("Outcome SD (optional, for raw-unit MDES)", min_value=0.0, value=0.0, step=0.1)
    outcome_sd = sd_input if sd_input > 0 else None

st.divider()

# ── Calculation ───────────────────────────────────────────────────────────────
calc_error: Optional[str] = None
result: Optional[MDESResult] = None

try:
    if is_cra3_3:
        result = compute_mdes_cra3_3(
            n_level3=int(n_level3),
            n_level2=int(n_level2),
            cluster_size=int(cluster_size),
            icc3=icc3,
            icc2=icc2,
            r2_level1=r2_level1,
            r2_level2=r2_level2,
            r2_level3=r2_level3,
            p_treat=p_treat,
            alpha=alpha,
            power=power,
            outcome_type=outcome_type,
            baseline_prob=baseline_prob,
            outcome_sd=outcome_sd,
        )
    else:
        result = compute_mdes_bcra3_2(
            n_level3=int(n_level3),
            n_level2=int(n_level2),
            cluster_size=int(cluster_size),
            icc3=icc3,
            icc2=icc2,
            r2_level1=r2_level1,
            r2_level2=r2_level2,
            p_treat=p_treat,
            alpha=alpha,
            power=power,
            outcome_type=outcome_type,
            baseline_prob=baseline_prob,
            outcome_sd=outcome_sd,
        )
except ValueError as exc:
    calc_error = str(exc)

# ── Results panel ─────────────────────────────────────────────────────────────
st.header("📊 Results")

if calc_error:
    st.error(f"⚠️ Input error: {calc_error}")
elif result is not None:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MDES (standardized)", f"{result.mdes:.3f}", help="Cohen's d")
    m2.metric("Standard error (σ_δ)", f"{result.se:.4f}")
    m3.metric("Degrees of freedom", f"{result.df}")
    m4.metric("Total sample size", f"{result.total_n:,}")

    m5, m6, m7 = st.columns(3)
    m5.metric("Design effect (DEFF)", f"{result.design_effect:.2f}")
    m6.metric("Effective N", f"{result.effective_n:,.0f}")
    if result.mdes_pct_points is not None:
        m7.metric("MDES (% points)", f"{result.mdes_pct_points:.2f} pp")
    elif result.mdes_raw is not None:
        m7.metric("MDES (raw units)", f"{result.mdes_raw:.3f}")

    st.info(f"💡 **Interpretation:** {result.interpretation}")

    # ── Visualisation ─────────────────────────────────────────────────────
    st.subheader("📈 MDES vs. Number of Level-3 Units")
    k_range = list(range(3, max(int(n_level3) * 3 + 1, 40)))
    mdes_curve: list[float] = []
    for k in k_range:
        try:
            if is_cra3_3:
                r = compute_mdes_cra3_3(
                    n_level3=k, n_level2=int(n_level2), cluster_size=int(cluster_size),
                    icc3=icc3, icc2=icc2, r2_level1=r2_level1, r2_level2=r2_level2,
                    r2_level3=r2_level3, p_treat=p_treat, alpha=alpha, power=power,
                )
            else:
                r = compute_mdes_bcra3_2(
                    n_level3=k, n_level2=int(n_level2), cluster_size=int(cluster_size),
                    icc3=icc3, icc2=icc2, r2_level1=r2_level1, r2_level2=r2_level2,
                    p_treat=p_treat, alpha=alpha, power=power,
                )
            mdes_curve.append(r.mdes)
        except ValueError:
            mdes_curve.append(float("nan"))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(k_range, mdes_curve, color="steelblue", label="MDES")
    ax.axvline(n_level3, color="red", linestyle="--", alpha=0.7, label="Current K")
    ax.axhline(result.mdes, color="green", linestyle=":", alpha=0.7, label="Current MDES")
    ax.set_xlabel("Number of level-3 units (K)")
    ax.set_ylabel("MDES (standardized)")
    ax.set_title(f"MDES vs K — {'CRA3_3' if is_cra3_3 else 'BCRA3_2'}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    # ── Download ──────────────────────────────────────────────────────────
    design_code = "CRA3_3" if is_cra3_3 else "BCRA3_2"
    summary_lines = [
        f"MDES Calculator – Three-Level CRT ({design_code})",
        "=" * 50,
        f"Level-3 units (K):             {n_level3}",
        f"Level-2 units per block (J):   {n_level2}",
        f"Cluster size (n):              {cluster_size}",
        f"ICC level 3 (rho3):            {icc3:.3f}",
        f"ICC level 2 (rho2):            {icc2:.3f}",
        f"R2 level-1:                    {r2_level1:.3f}",
        f"R2 level-2:                    {r2_level2:.3f}",
    ]
    if is_cra3_3:
        summary_lines.append(f"R2 level-3:                    {r2_level3:.3f}")
    summary_lines += [
        f"Proportion treated (P):        {p_treat:.2f}",
        f"Alpha:                         {alpha:.2f}",
        f"Power:                         {power:.0%}",
        f"Outcome type:                  {outcome_type}",
        "",
        "Results",
        "-" * 50,
        f"MDES (standardized):           {result.mdes:.4f}",
        f"Standard error:                {result.se:.4f}",
        f"Degrees of freedom:            {result.df}",
        f"Design effect (DEFF):          {result.design_effect:.3f}",
        f"Effective sample size:         {result.effective_n:.1f}",
        f"Total sample size:             {result.total_n}",
    ]
    if result.mdes_pct_points is not None:
        summary_lines.append(f"MDES (% points):               {result.mdes_pct_points:.2f} pp")
    if result.mdes_raw is not None:
        summary_lines.append(f"MDES (raw units):              {result.mdes_raw:.4f}")
    summary_lines += ["", result.interpretation]

    st.download_button(
        "Download summary (TXT)",
        data="\n".join(summary_lines),
        file_name=f"mdes_{design_code.lower()}_results.txt",
        mime="text/plain",
    )

st.divider()
st.caption("← Return to the [home page](/) to change design.")

"""
Two-Level CRT Calculator page (CRA2_2).

Clusters (e.g., classrooms or schools) are randomly assigned to treatment or
control.  Individuals (e.g., students) are nested within clusters.
"""

from __future__ import annotations

import io
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import math

from mdes_engines import compute_mdes_cra2_2
from mdes_engines.mdes_two_level import MDESResult, mdes_vs_clusters

import streamlit as st
import math

# 1. Read outcome type FIRST
outcome_type = st.session_state.get("outcome_type", "continuous")

# 2. Read design-specific defaults from session state
n_clusters = st.session_state.get("n_clusters", 20)
cluster_size = st.session_state.get("cluster_size", 20)
icc = st.session_state.get("icc", 0.10)
effect_size = st.session_state.get("effect_size", 0.20)
alpha = st.session_state.get("alpha", 0.05)
power = st.session_state.get("power", 0.80)
r2_level1 = st.session_state.get("r2_level1", 0.0)
r2_level2 = st.session_state.get("r2_level2", 0.0)

# 3. Read outcome-type-specific defaults
baseline_prob = st.session_state.get("baseline_prob", 0.50)
outcome_sd_input = st.session_state.get("outcome_sd_input", None)

st.set_page_config(
    page_title="Two-Level CRT – MDES Calculator",
    page_icon="🏫",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏫 Two-Level Cluster Randomized Trial")
st.subheader("Design: CRA2_2 — Clusters randomized, individuals nested within")
st.write(
    "Use this page when *whole* classrooms, clinics, or other groups are "
    "randomly assigned to treatment or control.  The formula accounts for "
    "within-cluster similarity (ICC) and optional covariates at each level."
)

with st.expander("📖 Statistical background"):
    st.markdown(
        r"""
**Model:** $Y_{ij} = \beta_0 + \delta T_j + u_j + e_{ij}$

**MDES formula** (Bloom et al., 2007; Dong & Maynard, 2013):

$$
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho\,(1 - R^2_2)}{P(1-P)\,J}
    +\frac{(1-\rho)\,(1 - R^2_1)}{P(1-P)\,J\,n}
}
$$

where $M_{\alpha,\nu} = t_{1-\alpha/2,\,\nu} + t_{\text{power},\,\nu}$,
$\nu = J - 2$, $\rho$ = ICC, $J$ = clusters, $n$ = cluster size,
$P$ = proportion treated, $R^2_1$ and $R^2_2$ are explained variance at
each level.
"""
    )

st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
st.header("⚙️ Study parameters")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Sample size")
    n_clusters = st.number_input(
        "Number of clusters (J)",
        value=n_clusters,
        min_value=3,
        max_value=10_000,
        step=1,
        help="Total number of clusters (e.g., schools, classrooms) in the study.",
    )
    cluster_size = st.number_input(
        "Average cluster size (n)",
        value=cluster_size,
        min_value=1,
        max_value=10_000,
        step=1,
        help="Average number of individuals per cluster.",
    )
    p_treat = st.slider(
        "Proportion assigned to treatment (P)",
        min_value=0.1,
        max_value=0.9,
        value=0.5,
        step=0.05,
        help="Proportion of clusters randomly assigned to the treatment arm.",
    )

with col_right:
    st.subheader("ICC & covariates")
    icc = st.slider(
        "Intraclass correlation (ρ)",
        min_value=0.00,
        max_value=0.50,
        value=icc,
        step=0.01,
        format="%.2f",
        help="Proportion of total outcome variance attributable to between-cluster differences.",
    )
    r2_level2 = st.slider(
        "Cluster-level covariate R² (R²₂)",
        min_value=0.00,
        max_value=0.99,
        value=r2_level2,
        step=0.01,
        format="%.2f",
    )
    r2_level1 = st.slider(
        "Individual-level covariate R² (R²₁)",
        min_value=0.00,
        max_value=0.99,
        value=r2_level1,
        step=0.01,
        format="%.2f",
    )

st.subheader("Statistical test settings")
col_a, col_b, col_c = st.columns(3)
with col_a:
    alpha = st.selectbox(
        "Significance level (α)",
        options=[0.01, 0.05, 0.10],
        index=[0.01, 0.05, 0.10].index(alpha),
    )
with col_b:
    power = st.selectbox(
        "Statistical power (1 − β)",
        options=[0.70, 0.75, 0.80, 0.85, 0.90],
        index=[0.70, 0.75, 0.80, 0.85, 0.90].index(power),
    )

# ── Outcome type ──────────────────────────────────────────────────────────────
st.subheader("Outcome type")

# Sync radio with session state
outcome_type = st.radio(
    "Outcome type",
    options=["continuous", "binary"],
    index=0 if outcome_type == "continuous" else 1,
    horizontal=True,
    label_visibility="collapsed",
)

# Clean irrelevant state
if outcome_type == "binary":
    st.session_state.outcome_sd_input = None
else:
    st.session_state.baseline_prob = None

# Outcome-specific widgets
if outcome_type == "binary":
    baseline_prob = st.slider(
        "Baseline event probability (p₀)",
        min_value=0.01,
        max_value=0.99,
        value=baseline_prob,
        step=0.01,
        format="%.2f",
    )
    outcome_sd = math.sqrt(baseline_prob * (1 - baseline_prob))

else:
    outcome_sd_input = st.number_input(
        "Outcome standard deviation (optional, for raw-unit MDES)",
        min_value=0.0,
        value=outcome_sd_input if outcome_sd_input is not None else 1.0,
        step=0.1,
    )
    outcome_sd = (
        outcome_sd_input
        if outcome_sd_input is not None and outcome_sd_input > 0
        else None
    )

# ── Calculation ───────────────────────────────────────────────────────────────
try:
    result: MDESResult = compute_mdes_cra2_2(
        n_clusters=int(n_clusters),
        cluster_size=int(cluster_size),
        icc=icc,
        r2_level1=r2_level1,
        r2_level2=r2_level2,
        p_treat=p_treat,
        alpha=alpha,
        power=power,
        outcome_type=outcome_type,
        baseline_prob=baseline_prob,
        outcome_sd=outcome_sd,
    )
    calc_error: Optional[str] = None
except ValueError as exc:
    result = None  # type: ignore[assignment]
    calc_error = str(exc)

# ── Results panel ─────────────────────────────────────────────────────────────
st.header("📊 Results")

if calc_error:
    st.error(f"⚠️ Input error: {calc_error}")
else:
    # Key metrics row
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
    st.subheader("📈 MDES vs. Number of Clusters")
    j_range = list(range(3, max(int(n_clusters) * 2 + 1, 60)))
    curves = mdes_vs_clusters(
        cluster_sizes=[cluster_size, cluster_size * 2],
        n_clusters_range=range(3, max(int(n_clusters) * 2 + 1, 60)),
        icc=icc,
        r2_level1=r2_level1,
        r2_level2=r2_level2,
        p_treat=p_treat,
        alpha=alpha,
        power=power,
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    for cs, vals in curves.items():
        ax.plot(j_range, vals, label=f"n = {cs}")
    ax.axvline(n_clusters, color="red", linestyle="--", alpha=0.7, label="Current J")
    ax.axhline(result.mdes, color="green", linestyle=":", alpha=0.7, label="Current MDES")
    ax.set_xlabel("Number of clusters (J)")
    ax.set_ylabel("MDES (standardized)")
    ax.set_title("MDES as a function of number of clusters")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    # ── Download ──────────────────────────────────────────────────────────
    st.subheader("⬇️ Download results")
    summary_lines = [
        "MDES Calculator – Two-Level CRT (CRA2_2)",
        "=" * 45,
        f"Number of clusters (J):        {n_clusters}",
        f"Cluster size (n):              {cluster_size}",
        f"ICC (rho):                     {icc:.3f}",
        f"R2 level-1:                    {r2_level1:.3f}",
        f"R2 level-2:                    {r2_level2:.3f}",
        f"Proportion treated (P):        {p_treat:.2f}",
        f"Alpha:                         {alpha:.2f}",
        f"Power:                         {power:.0%}",
        f"Outcome type:                  {outcome_type}",
        "",
        "Results",
        "-" * 45,
        f"MDES (standardized):           {result.mdes:.4f}",
        f"Standard error (sigma_delta):  {result.se:.4f}",
        f"Degrees of freedom:            {result.df}",
        f"Design effect (DEFF):          {result.design_effect:.3f}",
        f"Effective sample size:         {result.effective_n:.1f}",
        f"Total sample size:             {result.total_n}",
    ]
    if result.mdes_pct_points is not None:
        summary_lines.append(
            f"MDES (percentage points):      {result.mdes_pct_points:.2f} pp"
        )
    if result.mdes_raw is not None:
        summary_lines.append(
            f"MDES (raw units):              {result.mdes_raw:.4f}"
        )
    summary_lines += ["", result.interpretation]
    summary_text = "\n".join(summary_lines)

    st.download_button(
        label="Download summary (TXT)",
        data=summary_text,
        file_name="mdes_two_level_results.txt",
        mime="text/plain",
    )

st.divider()
st.caption("← Return to the [home page](/) to change design.")

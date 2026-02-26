"""
Blocked Two-Level CRT Calculator page (BCRA2_2).

Clusters are randomly assigned to treatment or control *within* pre-defined
blocks.  Blocks are treated as fixed effects, improving precision by removing
between-block variance from the error term.
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import streamlit as st

from mdes_engines import compute_mdes_bcra2_2
from mdes_engines.mdes_two_level import MDESResult

st.set_page_config(
    page_title="Blocked Two-Level CRT – MDES Calculator",
    page_icon="🧩",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧩 Blocked Two-Level CRT")
st.subheader("Design: BCRA2_2 — Clusters randomized within blocks")
st.write(
    "Use this page when clusters (e.g., classrooms or schools) are randomly "
    "assigned to treatment *within* pre-existing groupings called blocks "
    "(e.g., grade levels, geographic regions, or study waves).  Blocking "
    "absorbs between-block variance and can improve power."
)

with st.expander("📖 Statistical background"):
    st.markdown(
        r"""
**BCRA2_2 formula** (Dong & Maynard, 2013):

$$
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho\,(1 - R^2_2)}{P(1-P)\,J}
    +\frac{(1-\rho)\,(1 - R^2_1)}{P(1-P)\,J\,n}
}
$$

The **degrees of freedom** are adjusted for blocking:
$$\nu = J - 2B$$

where $B$ is the number of blocks.  This formula is identical to CRA2_2
except for the df adjustment: each block "costs" one degree of freedom.
"""
    )

st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
st.header("⚙️ Study parameters")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Sample size")
    n_blocks = st.number_input(
        "Number of blocks (B)",
        min_value=1,
        max_value=500,
        value=5,
        step=1,
        help="Number of blocks within which randomization occurs (e.g., 5 geographic regions).",
    )
    n_clusters = st.number_input(
        "Total number of clusters (J)",
        min_value=3,
        max_value=10_000,
        value=40,
        step=1,
        help="Total clusters across all blocks.  Must be > 2·B.",
    )
    cluster_size = st.number_input(
        "Average cluster size (n)",
        min_value=1,
        max_value=10_000,
        value=25,
        step=1,
    )
    p_treat = st.slider("Proportion assigned to treatment (P)", 0.1, 0.9, 0.5, 0.05)

with col_right:
    st.subheader("ICC & covariates")
    icc = st.slider(
        "Intraclass correlation (ρ)",
        0.00, 0.50, 0.10, 0.01,
        format="%.2f",
        help="Typical education values: 0.05–0.20.",
    )
    r2_level2 = st.slider("Cluster-level covariate R² (R²₂)", 0.00, 0.99, 0.00, 0.01, format="%.2f")
    r2_level1 = st.slider("Individual-level covariate R² (R²₁)", 0.00, 0.99, 0.00, 0.01, format="%.2f")

    # Validation hint
    min_clusters = 2 * n_blocks + 1
    if n_clusters <= 2 * n_blocks:
        st.warning(
            f"⚠️ Total clusters (J = {n_clusters}) must be > 2·B = {2 * n_blocks}.  "
            f"Increase J to at least {min_clusters}."
        )

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
    sd_input = st.number_input("Outcome SD (optional)", min_value=0.0, value=0.0, step=0.1)
    outcome_sd = sd_input if sd_input > 0 else None

st.divider()

# ── Calculation ───────────────────────────────────────────────────────────────
calc_error: Optional[str] = None
result: Optional[MDESResult] = None

try:
    result = compute_mdes_bcra2_2(
        n_clusters=int(n_clusters),
        cluster_size=int(cluster_size),
        n_blocks=int(n_blocks),
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

    # ── Blocking comparison ────────────────────────────────────────────────
    st.subheader("📊 Effect of blocking on MDES")

    # Compare MDES with vs without blocking for current settings
    from mdes_engines import compute_mdes_cra2_2

    try:
        result_unblocked = compute_mdes_cra2_2(
            n_clusters=int(n_clusters),
            cluster_size=int(cluster_size),
            icc=icc,
            r2_level1=r2_level1,
            r2_level2=r2_level2,
            p_treat=p_treat,
            alpha=alpha,
            power=power,
        )
        unblocked_mdes = result_unblocked.mdes
    except ValueError:
        unblocked_mdes = None

    if unblocked_mdes is not None:
        col_cmp1, col_cmp2, col_cmp3 = st.columns(3)
        col_cmp1.metric("Without blocking (CRA2_2)", f"{unblocked_mdes:.3f}")
        col_cmp2.metric("With blocking (BCRA2_2)", f"{result.mdes:.3f}")
        delta = unblocked_mdes - result.mdes
        col_cmp3.metric(
            "MDES reduction from blocking",
            f"{abs(delta):.3f}",
            delta=f"{'↓' if delta > 0 else '↑'} {abs(delta):.3f}",
            delta_color="normal" if delta > 0 else "inverse",
        )

    # ── Visualisation ─────────────────────────────────────────────────────
    st.subheader("📈 MDES vs. Number of Clusters")
    j_range = list(range(max(2 * int(n_blocks) + 1, 3), max(int(n_clusters) * 2 + 1, 60)))
    mdes_blocked_curve: list[float] = []
    mdes_unblocked_curve: list[float] = []

    for j in j_range:
        try:
            rb = compute_mdes_bcra2_2(
                n_clusters=j, cluster_size=int(cluster_size), n_blocks=int(n_blocks),
                icc=icc, r2_level1=r2_level1, r2_level2=r2_level2,
                p_treat=p_treat, alpha=alpha, power=power,
            )
            mdes_blocked_curve.append(rb.mdes)
        except ValueError:
            mdes_blocked_curve.append(float("nan"))
        try:
            ru = compute_mdes_cra2_2(
                n_clusters=j, cluster_size=int(cluster_size),
                icc=icc, r2_level1=r2_level1, r2_level2=r2_level2,
                p_treat=p_treat, alpha=alpha, power=power,
            )
            mdes_unblocked_curve.append(ru.mdes)
        except ValueError:
            mdes_unblocked_curve.append(float("nan"))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(j_range, mdes_blocked_curve, label=f"Blocked (B={n_blocks})", color="steelblue")
    ax.plot(j_range, mdes_unblocked_curve, label="Unblocked (CRA2_2)", color="orange", linestyle="--")
    ax.axvline(n_clusters, color="red", linestyle=":", alpha=0.7, label="Current J")
    ax.set_xlabel("Number of clusters (J)")
    ax.set_ylabel("MDES (standardized)")
    ax.set_title("MDES comparison: blocked vs. unblocked")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    # ── Download ──────────────────────────────────────────────────────────
    summary_lines = [
        "MDES Calculator – Blocked Two-Level CRT (BCRA2_2)",
        "=" * 50,
        f"Number of blocks (B):          {n_blocks}",
        f"Total clusters (J):            {n_clusters}",
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
        file_name="mdes_bcra2_2_results.txt",
        mime="text/plain",
    )

st.divider()
st.caption("← Return to the [home page](/) to change design.")

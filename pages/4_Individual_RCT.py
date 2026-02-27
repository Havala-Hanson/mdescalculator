"""
Individual-level randomized trial page (INDIV_RCT).

Supports MDES calculation and required sample size for two-arm trials with
optional unequal allocation and covariate adjustment via R².
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from mdes_engines import compute_mdes_indiv_rct, required_n_for_mdes
from mdes_engines.mdes_individual import IndividualMDESResult

st.set_page_config(
    page_title="Individual-Level RCT – MDES Calculator",
    page_icon="🧍",
    layout="wide",
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🧍 Individual-Level Randomized Trial")
st.subheader("Design: INDIV_RCT — Participants individually randomized to two arms")
st.write(
    "Use this page for studies where individual participants are randomly "
    "assigned to treatment or control with no clustering.  You can compute "
    "the MDES for a given sample size or solve for the required sample size "
    "to hit a target MDES."
)

with st.expander("📖 Statistical background"):
    st.markdown(
        r"""
**Model:** $Y_i = \beta_0 + \delta T_i + e_i$

**Standard error** for the standardized effect estimator:
$$
\sigma_\delta = \sqrt{\frac{1 - R^2}{P(1-P)\,N}}
$$

where $P$ is the treatment allocation proportion, $N$ is total sample size,
and $R^2$ is variance explained by covariates.

**MDES:** $\text{MDES} = M_{\alpha,\nu} \cdot \sigma_\delta$ with
$M_{\alpha,\nu} = t_{1-\alpha/2,\nu} + t_{\text{power},\nu}$ and
$\nu = N - 2$.
"""
    )

st.divider()

# ── Inputs ───────────────────────────────────────────────────────────────────
st.header("⚙️ Study parameters")

mode = st.radio(
    "What would you like to compute?",
    options=["Compute MDES", "Compute required N"],
    index=0,
    horizontal=True,
)

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Design settings")
    allocation_ratio = st.number_input(
        "Allocation ratio (n_treat / n_control)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
        help="1 = equal allocation. Values > 1 put more participants in treatment.",
    )
    r2 = st.slider(
        "Covariate R²",
        min_value=0.00,
        max_value=0.90,
        value=0.00,
        step=0.01,
        format="%.2f",
        help="Proportion of outcome variance explained by covariates included in the model.",
    )

with col_right:
    st.subheader("Test settings")
    alpha = st.selectbox(
        "Significance level (α)",
        options=[0.01, 0.05, 0.10],
        index=1,
        format_func=lambda x: f"{x:.2f}",
    )
    power = st.selectbox(
        "Statistical power (1 − β)",
        options=[0.70, 0.75, 0.80, 0.85, 0.90],
        index=2,
        format_func=lambda x: f"{x:.0%}",
    )

st.subheader("Outcome type")
outcome_type = st.radio(
    "Outcome type",
    options=["continuous", "binary"],
    index=0,
    horizontal=True,
    label_visibility="collapsed",
)

baseline_prob: Optional[float] = None
outcome_sd: Optional[float] = None

if outcome_type == "binary":
    baseline_prob = st.slider(
        "Baseline event probability (p₀)",
        min_value=0.01,
        max_value=0.99,
        value=0.30,
        step=0.01,
        format="%.2f",
        help="Expected proportion experiencing the outcome in the control group.",
    )
else:
    sd_input = st.number_input(
        "Outcome standard deviation (optional, for raw-unit MDES)",
        min_value=0.0,
        value=0.0,
        step=0.1,
    )
    outcome_sd = sd_input if sd_input > 0 else None

st.divider()

# ── Compute MDES or N ───────────────────────────────────────────────────────
result: Optional[IndividualMDESResult] = None
calc_error: Optional[str] = None

if mode == "Compute MDES":
    total_n = st.number_input(
        "Total sample size (N)",
        min_value=4,
        max_value=1_000_000,
        value=200,
        step=10,
    )
    try:
        result = compute_mdes_indiv_rct(
            total_n=int(total_n),
            allocation_ratio=allocation_ratio,
            r2=r2,
            alpha=alpha,
            power=power,
            outcome_type=outcome_type,
            baseline_prob=baseline_prob,
            outcome_sd=outcome_sd,
        )
    except ValueError as exc:
        calc_error = str(exc)
else:
    target_mdes = st.number_input(
        "Target MDES (standardized)",
        min_value=0.01,
        max_value=2.0,
        value=0.20,
        step=0.01,
        format="%.2f",
    )
    try:
        required_n = required_n_for_mdes(
            target_mdes=float(target_mdes),
            allocation_ratio=allocation_ratio,
            r2=r2,
            alpha=alpha,
            power=power,
        )
        # Compute MDES at that N to show resulting stats
        result = compute_mdes_indiv_rct(
            total_n=required_n,
            allocation_ratio=allocation_ratio,
            r2=r2,
            alpha=alpha,
            power=power,
            outcome_type=outcome_type,
            baseline_prob=baseline_prob,
            outcome_sd=outcome_sd,
        )
    except ValueError as exc:
        calc_error = str(exc)

# ── Results ─────────────────────────────────────────────────────────────────
st.header("📊 Results")

if calc_error:
    st.error(f"⚠️ Input error: {calc_error}")
elif result is not None:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MDES (standardized)", f"{result.mdes:.3f}")
    m2.metric("Standard error (σ_δ)", f"{result.se:.4f}")
    m3.metric("Degrees of freedom", f"{result.df}")
    m4.metric("Total sample size", f"{result.total_n:,}")

    m5, m6 = st.columns(2)
    m5.metric("Allocation ratio", f"{result.allocation_ratio:.2f}")
    if result.mdes_pct_points is not None:
        m6.metric("MDES (% points)", f"{result.mdes_pct_points:.2f} pp")
    elif result.mdes_raw is not None:
        m6.metric("MDES (raw units)", f"{result.mdes_raw:.3f}")

    st.info(f"💡 **Interpretation:** {result.interpretation}")

    # Summary text for download
    summary_lines = [
        "MDES Calculator – Individual-Level RCT (INDIV_RCT)",
        "=" * 55,
        f"Mode:                      {mode}",
        f"Total sample size (N):     {result.total_n}",
        f"Allocation ratio (nT/nC):  {result.allocation_ratio:.3f}",
        f"Covariate R2:              {r2:.3f}",
        f"Alpha:                     {alpha:.2f}",
        f"Power:                     {power:.0%}",
        f"Outcome type:              {outcome_type}",
    ]
    if outcome_type == "binary" and baseline_prob is not None:
        summary_lines.append(f"Baseline probability (p0): {baseline_prob:.2f}")
    if outcome_type == "continuous" and outcome_sd is not None:
        summary_lines.append(f"Outcome SD: {outcome_sd:.3f}")
    summary_lines += [
        "",
        "Results",
        "-" * 55,
        f"MDES (standardized):       {result.mdes:.4f}",
        f"Standard error:            {result.se:.4f}",
        f"Degrees of freedom:        {result.df}",
    ]
    if result.mdes_pct_points is not None:
        summary_lines.append(f"MDES (% points):           {result.mdes_pct_points:.2f} pp")
    if result.mdes_raw is not None:
        summary_lines.append(f"MDES (raw units):          {result.mdes_raw:.4f}")
    summary_lines.append("")
    summary_lines.append(result.interpretation)

    st.download_button(
        label="Download summary (TXT)",
        data="\n".join(summary_lines),
        file_name="mdes_individual_rct.txt",
        mime="text/plain",
    )

st.divider()
st.caption("← Return to the [home page](/) to change design.")

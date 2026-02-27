"""
Individual-level randomized trial MDES engine.

Design: INDIV_RCT
-----------------
Participants are individually randomized to two arms with an optional
unequal allocation ratio.  Covariate adjustment enters via R².

Formula (standard two-sample t-test with pooled variance):
    σ_δ = sqrt[(1 - R²) / (P(1-P)·N)]
    M   = t_{1-α/2, df} + t_{power, df}, where df = N − 2
    MDES = M · σ_δ

Required N for a target MDES can be solved in closed form if M is treated as
constant, but since M depends on df, we iterate until convergence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from scipy import stats


@dataclass
class IndividualMDESResult:
    """Outputs for the INDIV_RCT design."""

    mdes: float
    se: float
    df: int
    total_n: int
    allocation_ratio: float
    mdes_pct_points: Optional[float] = None
    mdes_raw: Optional[float] = None
    interpretation: str = ""


def _multiplier(alpha: float, power: float, df: int) -> float:
    effective_df = max(df, 1)
    return float(
        stats.t.ppf(1.0 - alpha / 2.0, effective_df)
        + stats.t.ppf(power, effective_df)
    )


def _interpret_mdes(mdes: float) -> str:
    if mdes <= 0.2:
        label = "small"
    elif mdes <= 0.5:
        label = "small-to-medium"
    elif mdes <= 0.8:
        label = "medium-to-large"
    else:
        label = "large"
    return (
        f"Your study can detect a {label} effect (d ≈ {mdes:.2f}). "
        "Increasing N, balancing allocation, or adding covariates will lower the MDES."
    )


def compute_mdes_indiv_rct(
    total_n: int,
    allocation_ratio: float = 1.0,
    r2: float = 0.0,
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: Optional[float] = None,
    outcome_sd: Optional[float] = None,
) -> IndividualMDESResult:
    """Compute MDES for an individually randomized two-arm trial.

    Parameters
    ----------
    total_n: int
        Total sample size N (treatment + control).  Must be ≥ 4.
    allocation_ratio: float
        Ratio n_treatment / n_control.  1.0 = equal allocation.
    r2: float
        Proportion of outcome variance explained by covariates.
    alpha, power: float
        Two-sided alpha and desired power.
    outcome_type: str
        "continuous" or "binary".
    baseline_prob: Optional[float]
        Baseline event probability for binary outcomes.
    outcome_sd: Optional[float]
        Outcome SD to report MDES in raw units for continuous outcomes.
    """

    if total_n < 4:
        raise ValueError("total_n must be at least 4.")
    if allocation_ratio <= 0:
        raise ValueError("allocation_ratio must be > 0.")
    if not 0.0 <= r2 < 1.0:
        raise ValueError("r2 must be in [0, 1).")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1).")
    if not 0.0 < power < 1.0:
        raise ValueError("power must be in (0, 1).")
    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        if not 0.0 < baseline_prob < 1.0:
            raise ValueError("baseline_prob must be in (0, 1).")

    p_treat = allocation_ratio / (1.0 + allocation_ratio)
    p_control = 1.0 - p_treat

    df = total_n - 2
    se = math.sqrt((1.0 - r2) / (p_treat * p_control * total_n))
    M = _multiplier(alpha, power, df)
    mdes = M * se

    mdes_pct_points: Optional[float] = None
    mdes_raw: Optional[float] = None
    if outcome_type == "binary" and baseline_prob is not None:
        sigma_binary = math.sqrt(baseline_prob * (1.0 - baseline_prob))
        mdes_pct_points = mdes * sigma_binary * 100.0
    if outcome_type == "continuous" and outcome_sd is not None:
        mdes_raw = mdes * outcome_sd

    return IndividualMDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        total_n=total_n,
        allocation_ratio=round(allocation_ratio, 3),
        mdes_pct_points=(round(mdes_pct_points, 2) if mdes_pct_points else None),
        mdes_raw=round(mdes_raw, 4) if mdes_raw is not None else None,
        interpretation=_interpret_mdes(mdes),
    )


def required_n_for_mdes(
    target_mdes: float,
    allocation_ratio: float = 1.0,
    r2: float = 0.0,
    alpha: float = 0.05,
    power: float = 0.80,
    max_iter: int = 50,
    tol: float = 1e-4,
) -> int:
    """Solve for total N that attains the target MDES.

    Uses a simple fixed-point iteration on N because df (and hence M)
    depends on N.
    """

    if target_mdes <= 0:
        raise ValueError("target_mdes must be positive.")
    if allocation_ratio <= 0:
        raise ValueError("allocation_ratio must be > 0.")
    if not 0.0 <= r2 < 1.0:
        raise ValueError("r2 must be in [0, 1).")

    p_treat = allocation_ratio / (1.0 + allocation_ratio)
    p_control = 1.0 - p_treat

    # Start with a normal-approximation guess
    M_norm = stats.norm.ppf(1.0 - alpha / 2.0) + stats.norm.ppf(power)
    n_guess = (M_norm**2 * (1.0 - r2)) / (target_mdes**2 * p_treat * p_control)
    n_curr = max(int(math.ceil(n_guess)), 4)

    for _ in range(max_iter):
        df = max(n_curr - 2, 1)
        M = _multiplier(alpha, power, df)
        n_next = (M**2 * (1.0 - r2)) / (target_mdes**2 * p_treat * p_control)
        if abs(n_next - n_curr) < tol * n_curr:
            return int(math.ceil(n_next))
        n_curr = int(math.ceil((n_curr + n_next) / 2))

    return int(math.ceil(n_curr))

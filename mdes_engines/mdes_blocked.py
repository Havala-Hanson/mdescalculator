"""
Blocked two-level CRT MDES engine.

Design: BCRA2_2
---------------
Clusters (level-2 units) are randomly assigned to treatment or control
*within* blocks.  Blocks (e.g., regions, cohorts, strata) are treated as
fixed effects, so block-level variance does not inflate the treatment
variance.

Formula (Dong & Maynard, 2013 / PowerUp!)
------------------------------------------
σ_δ = sqrt[ ρ(1 − R²₂) / (P(1−P)·J)
          + (1 − ρ)(1 − R²₁) / (P(1−P)·J·n) ]

df  = J − 2·B

where
    ρ   = ICC at level 2
    R²₁, R²₂ = R² at each level
    P   = proportion assigned to treatment
    J   = total number of clusters
    n   = average cluster size
    B   = number of blocks

The formula is identical to CRA2_2 except for the degrees-of-freedom
adjustment: each block uses one additional degree of freedom.

References
----------
Dong, N., & Maynard, R. A. (2013). PowerUp!: A tool for calculating minimum
detectable effect sizes and minimum required sample sizes for experimental and
quasi-experimental design studies. Journal of Research on Educational
Effectiveness, 6(1), 24–67.
"""

from __future__ import annotations

import math
from typing import Optional

from .mdes_two_level import MDESResult, _interpret_mdes, _multiplier, _se_cra2_2


def compute_mdes_bcra2_2(
    n_clusters: int,
    cluster_size: int,
    n_blocks: int,
    icc: float,
    r2_level1: float = 0.0,
    r2_level2: float = 0.0,
    p_treat: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: Optional[float] = None,
    outcome_sd: Optional[float] = None,
) -> MDESResult:
    """Compute the MDES for a two-level blocked CRT (BCRA2_2).

    Parameters
    ----------
    n_clusters:
        Total number of clusters J across all blocks.  Must be > 2·n_blocks.
    cluster_size:
        Average number of individuals per cluster n.  Must be ≥ 1.
    n_blocks:
        Number of blocks B.  Must be ≥ 1.
    icc:
        Intraclass correlation ρ ∈ [0, 1).
    r2_level1:
        R² at level 1 from individual covariates (default 0).
    r2_level2:
        R² at level 2 from cluster covariates (default 0).
    p_treat:
        Proportion of clusters assigned to treatment per block.  Defaults
        to 0.5.
    alpha:
        Two-sided significance level.  Defaults to 0.05.
    power:
        Desired statistical power.  Defaults to 0.80.
    outcome_type:
        ``"continuous"`` or ``"binary"``.
    baseline_prob:
        Baseline event probability (required for binary outcomes).
    outcome_sd:
        Outcome SD in raw units (optional, continuous only).

    Returns
    -------
    MDESResult
        Dataclass with MDES and related statistics.

    Raises
    ------
    ValueError
        If inputs are outside valid ranges or df ≤ 0.
    """
    # ── Validation ────────────────────────────────────────────────────────
    if n_blocks < 1:
        raise ValueError("n_blocks must be at least 1.")
    if n_clusters <= 2 * n_blocks:
        raise ValueError(
            "n_clusters must be greater than 2·n_blocks to ensure df > 0."
        )
    if cluster_size < 1:
        raise ValueError("cluster_size must be at least 1.")
    if not 0.0 <= icc < 1.0:
        raise ValueError("icc must be in [0, 1).")
    if not 0.0 <= r2_level1 < 1.0:
        raise ValueError("r2_level1 must be in [0, 1).")
    if not 0.0 <= r2_level2 < 1.0:
        raise ValueError("r2_level2 must be in [0, 1).")
    if not 0.0 < p_treat < 1.0:
        raise ValueError("p_treat must be in (0, 1).")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1).")
    if not 0.0 < power < 1.0:
        raise ValueError("power must be in (0, 1).")
    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        if not 0.0 < baseline_prob < 1.0:
            raise ValueError("baseline_prob must be in (0, 1).")

    # ── Calculation ───────────────────────────────────────────────────────
    # df is reduced by n_blocks (one df per block mean estimated)
    df = n_clusters - 2 * n_blocks
    se = _se_cra2_2(icc, r2_level1, r2_level2, p_treat, n_clusters, cluster_size)
    M = _multiplier(alpha, power, df)
    mdes = M * se

    total_n = n_clusters * cluster_size
    design_effect = 1.0 + (cluster_size - 1) * icc
    effective_n = total_n / design_effect

    mdes_pct_points: Optional[float] = None
    mdes_raw: Optional[float] = None
    if outcome_type == "binary" and baseline_prob is not None:
        sigma_binary = math.sqrt(baseline_prob * (1.0 - baseline_prob))
        mdes_pct_points = mdes * sigma_binary * 100.0
    if outcome_type == "continuous" and outcome_sd is not None:
        mdes_raw = mdes * outcome_sd

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=round(design_effect, 3),
        effective_n=round(effective_n, 1),
        total_n=total_n,
        mdes_pct_points=(
            round(mdes_pct_points, 2) if mdes_pct_points is not None else None
        ),
        mdes_raw=round(mdes_raw, 4) if mdes_raw is not None else None,
        interpretation=_interpret_mdes(mdes),
    )

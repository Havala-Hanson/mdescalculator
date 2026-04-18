"""
Three-level Cluster Randomised Trial MDES engines.

Supported design
-----------------
CRA3_3  – Complete random assignment at level 3.

Formulas follow Dong & Maynard (2013).
"""

from __future__ import annotations

import math
from typing import Optional

from .mdes_two_level import MDESResult, _multiplier


# ── CRA3_3 ────────────────────────────────────────────────────────────────────

def _se_cra3_3(
    icc3: float,
    icc2: float,
    r2_level1: float,
    r2_level2: float,
    r2_level3: float,
    p_treat: float,
    n_level3: int,
    n_level2: int,
    cluster_size: int,
) -> float:
    denom_base = p_treat * (1.0 - p_treat)
    icc1 = max(0.0, 1.0 - icc3 - icc2)

    variance = (
        icc3 * (1.0 - r2_level3) / (denom_base * n_level3)
        + icc2 * (1.0 - r2_level2) / (denom_base * n_level3 * n_level2)
        + icc1 * (1.0 - r2_level1)
        / (denom_base * n_level3 * n_level2 * cluster_size)
    )
    return math.sqrt(max(variance, 0.0))


def compute_mdes_cra3_3(
    n_level3: int,
    n_level2: int,
    cluster_size: int,
    icc3: float,
    icc2: float,
    r2_level1: float = 0.0,
    r2_level2: float = 0.0,
    r2_level3: float = 0.0,
    p_treat: float = 0.5,
    g3: int = 0,
    two_tailed: bool = True,
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: Optional[float] = None,
    outcome_sd: Optional[float] = None,
) -> MDESResult:
    """
    MDES for three-level CRA randomised at level 3 (CRA3_3r).

    Mirrors R's mdes.cra3r3 (PowerUpR):

        df  = K - g3 - 2
        SSE = sqrt[
            ρ₃(1−R²₃) / (p(1-p)·K)
          + ρ₂(1−R²₂) / (p(1-p)·J·K)
          + ρ₁(1−R²₁) / (p(1-p)·J·K·n)
        ]

    Parameters
    ----------
    g3        : number of level-3 covariates for df adjustment (R: g3, default 0)
    two_tailed: use two-tailed critical value (R: two.tailed, default True)
    """

    if n_level3 < 3:
        raise ValueError("n_level3 must be at least 3.")
    if n_level2 < 1:
        raise ValueError("n_level2 must be at least 1.")
    if cluster_size < 1:
        raise ValueError("cluster_size must be at least 1.")
    if not 0.0 <= icc3 < 1.0:
        raise ValueError("icc3 must be in [0, 1).")
    if not 0.0 <= icc2 < 1.0:
        raise ValueError("icc2 must be in [0, 1).")
    if icc2 + icc3 >= 1.0:
        raise ValueError("icc2 + icc3 must be < 1.")
    for name, val in [
        ("r2_level1", r2_level1),
        ("r2_level2", r2_level2),
        ("r2_level3", r2_level3),
    ]:
        if not 0.0 <= val < 1.0:
            raise ValueError(f"{name} must be in [0, 1).")
    if not 0.0 < p_treat < 1.0:
        raise ValueError("p_treat must be in (0, 1).")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1).")
    if not 0.0 < power < 1.0:
        raise ValueError("power must be in (0, 1).")
    if g3 < 0:
        raise ValueError("g3 must be >= 0.")
    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        if not 0.0 < baseline_prob < 1.0:
            raise ValueError("baseline_prob must be in (0, 1).")

    # Match PowerUpR: df = K - g3 - 2 for CRA3_3r.
    df = n_level3 - g3 - 2
    se = _se_cra3_3(
        icc3, icc2, r2_level1, r2_level2, r2_level3,
        p_treat, n_level3, n_level2, cluster_size,
    )
    M = _multiplier(alpha, power, df, two_tailed=two_tailed)
    mdes = M * se

    total_n = n_level3 * n_level2 * cluster_size
    design_effect = (
        1.0
        + (cluster_size - 1) * icc2
        + (cluster_size * n_level2 - 1) * icc3
    )
    effective_n = total_n / design_effect

    mdes_pct_points = None
    mdes_standardized = None
    if outcome_type == "binary" and baseline_prob is not None:
        sigma_binary = math.sqrt(baseline_prob * (1.0 - baseline_prob))
        mdes_pct_points = mdes * sigma_binary * 100.0
    if outcome_type == "continuous" and outcome_sd is not None:
        mdes_standardized = mdes * outcome_sd

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=round(design_effect, 3),
        effective_n=round(effective_n, 1),
        total_n=total_n,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
        interpretation=None,
    )

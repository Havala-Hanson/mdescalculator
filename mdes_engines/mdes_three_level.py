"""
Three-level Cluster Randomised Trial MDES engines.

Supported designs
-----------------
CRA3_3  – Complete random assignment at level 3.
BCRA3_2 – Blocked CRT at level 2, level 3 as blocks.

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
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: Optional[float] = None,
    outcome_sd: Optional[float] = None,
) -> MDESResult:

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
    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        if not 0.0 < baseline_prob < 1.0:
            raise ValueError("baseline_prob must be in (0, 1).")

    df = n_level3 - 2
    se = _se_cra3_3(
        icc3, icc2, r2_level1, r2_level2, r2_level3,
        p_treat, n_level3, n_level2, cluster_size,
    )
    M = _multiplier(alpha, power, df)
    mdes = M * se

    total_n = n_level3 * n_level2 * cluster_size
    design_effect = (
        1.0
        + (cluster_size - 1) * icc2
        + (cluster_size * n_level2 - 1) * icc3
    )
    effective_n = total_n / design_effect

    mdes_pct_points = None
    mdes_raw = None
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
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_raw=round(mdes_raw, 4) if mdes_raw else None,
        interpretation=None,
    )


# ── BCRA3_2 ───────────────────────────────────────────────────────────────────

def _se_bcra3_2(
    icc3: float,
    icc2: float,
    r2_level1: float,
    r2_level2: float,
    p_treat: float,
    n_level3: int,
    n_level2: int,
    cluster_size: int,
) -> float:
    denom_base = p_treat * (1.0 - p_treat)
    icc1 = max(0.0, 1.0 - icc3 - icc2)

    variance = (
        icc2 * (1.0 - r2_level2) / (denom_base * n_level3 * n_level2)
        + icc1 * (1.0 - r2_level1)
        / (denom_base * n_level3 * n_level2 * cluster_size)
    )
    return math.sqrt(max(variance, 0.0))


def compute_mdes_bcra3_2(
    n_level3: int,
    n_level2: int,
    cluster_size: int,
    icc3: float,
    icc2: float,
    r2_level1: float = 0.0,
    r2_level2: float = 0.0,
    p_treat: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: Optional[float] = None,
    outcome_sd: Optional[float] = None,
) -> MDESResult:

    if n_level3 < 1:
        raise ValueError("n_level3 must be at least 1.")
    if n_level2 < 3:
        raise ValueError("n_level2 must be at least 3.")
    if cluster_size < 1:
        raise ValueError("cluster_size must be at least 1.")
    if not 0.0 <= icc3 < 1.0:
        raise ValueError("icc3 must be in [0, 1).")
    if not 0.0 <= icc2 < 1.0:
        raise ValueError("icc2 must be in [0, 1).")
    if icc2 + icc3 >= 1.0:
        raise ValueError("icc2 + icc3 must be < 1.")
    for name, val in [("r2_level1", r2_level1), ("r2_level2", r2_level2)]:
        if not 0.0 <= val < 1.0:
            raise ValueError(f"{name} must be in [0, 1).")
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

    df = n_level3 * (n_level2 - 2)
    se = _se_bcra3_2(
        icc3, icc2, r2_level1, r2_level2,
        p_treat, n_level3, n_level2, cluster_size,
    )
    M = _multiplier(alpha, power, df)
    mdes = M * se

    total_n = n_level3 * n_level2 * cluster_size
    design_effect = (
        1.0
        + (cluster_size - 1) * icc2
        + (cluster_size * n_level2 - 1) * icc3
    )
    effective_n = total_n / design_effect

    mdes_pct_points = None
    mdes_raw = None
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
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_raw=round(mdes_raw, 4) if mdes_raw else None,
        interpretation=None,
    )
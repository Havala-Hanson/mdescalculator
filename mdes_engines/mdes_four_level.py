"""
Four-level Cluster Randomised Trial MDES engines.

Supported designs
-----------------
CRA4_4 – Complete random assignment at level 4 (e.g., districts randomised).
(Used by CRA4_4 and CRA4_4r pages.)

Notation
--------
L4  = number of level-4 units (e.g., districts)
L3  = number of level-3 units per level-4 unit (e.g., schools per district)
L2  = number of level-2 units per level-3 unit (e.g., classrooms per school)
n   = number of level-1 units per level-2 unit (e.g., students per classroom)
ρ4  = ICC at level 4
ρ3  = ICC at level 3
ρ2  = ICC at level 2
ρ1  = 1 − ρ4 − ρ3 − ρ2
R²4 = R² at level 4 from covariates
R²3 = R² at level 3 from covariates
R²2 = R² at level 2 from covariates
R²1 = R² at level 1 from covariates
P   = proportion of units assigned to treatment

CRA4_4 variance (extension of Dong & Maynard, 2013)
---------------------------------------------------
σ_δ = sqrt[
    ρ4(1 − R²4) / (P(1−P)·L4)
  + ρ3(1 − R²3) / (P(1−P)·L4·L3)
  + ρ2(1 − R²2) / (P(1−P)·L4·L3·L2)
  + ρ1(1 − R²1) / (P(1−P)·L4·L3·L2·n)
]

df = L4 − 2
"""

from __future__ import annotations

import math
from typing import Optional

from .mdes_two_level import MDESResult, _multiplier


# ---------------------------------------------------------------------
# Helper: standard error for CRA4_4
# ---------------------------------------------------------------------

def _se_cra4_4(
    icc4: float,
    icc3: float,
    icc2: float,
    r2_level1: float,
    r2_level2: float,
    r2_level3: float,
    r2_level4: float,
    p_treat: float,
    n_level4: int,
    n_level3: int,
    n_level2: int,
    cluster_size: int,
) -> float:
    denom_base = p_treat * (1.0 - p_treat)
    icc1 = max(0.0, 1.0 - icc4 - icc3 - icc2)

    variance = (
        icc4 * (1.0 - r2_level4) / (denom_base * n_level4)
        + icc3 * (1.0 - r2_level3) / (denom_base * n_level4 * n_level3)
        + icc2 * (1.0 - r2_level2) / (denom_base * n_level4 * n_level3 * n_level2)
        + icc1 * (1.0 - r2_level1)
        / (denom_base * n_level4 * n_level3 * n_level2 * cluster_size)
    )
    return math.sqrt(max(variance, 0.0))


# ---------------------------------------------------------------------
# CRA4_4 engine (math only)
# ---------------------------------------------------------------------

def compute_mdes_cra4_4(
    n_level4: int,
    n_level3: int,
    n_level2: int,
    cluster_size: int,
    icc4: float,
    icc3: float,
    icc2: float,
    r2_level1: float = 0.0,
    r2_level2: float = 0.0,
    r2_level3: float = 0.0,
    r2_level4: float = 0.0,
    p_treat: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: Optional[float] = None,
    outcome_sd: Optional[float] = None,
) -> MDESResult:
    """
    Minimum detectable effect size for a four-level CRT randomised at level 4 (CRA4_4).

    Levels:
      - Level 4: highest level (e.g., districts)
      - Level 3: nested within level 4 (e.g., schools)
      - Level 2: nested within level 3 (e.g., classrooms)
      - Level 1: individuals (e.g., students)
    """

    # --- Validation ----------------------------------------------------
    if n_level4 < 3:
        raise ValueError("n_level4 must be at least 3.")
    if n_level3 < 1:
        raise ValueError("n_level3 must be at least 1.")
    if n_level2 < 1:
        raise ValueError("n_level2 must be at least 1.")
    if cluster_size < 1:
        raise ValueError("cluster_size must be at least 1.")

    for name, val in [
        ("icc4", icc4),
        ("icc3", icc3),
        ("icc2", icc2),
    ]:
        if not 0.0 <= val < 1.0:
            raise ValueError(f"{name} must be in [0, 1).")

    if icc4 + icc3 + icc2 >= 1.0:
        raise ValueError("icc4 + icc3 + icc2 must be < 1.")

    for name, val in [
        ("r2_level1", r2_level1),
        ("r2_level2", r2_level2),
        ("r2_level3", r2_level3),
        ("r2_level4", r2_level4),
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

    # --- Degrees of freedom -------------------------------------------
    df = n_level4 - 2
    if df <= 1:
        raise ValueError("Not enough level-4 units for valid degrees of freedom.")

    # --- Standard error and MDES --------------------------------------
    se = _se_cra4_4(
        icc4=icc4,
        icc3=icc3,
        icc2=icc2,
        r2_level1=r2_level1,
        r2_level2=r2_level2,
        r2_level3=r2_level3,
        r2_level4=r2_level4,
        p_treat=p_treat,
        n_level4=n_level4,
        n_level3=n_level3,
        n_level2=n_level2,
        cluster_size=cluster_size,
    )

    M = _multiplier(alpha, power, df)
    mdes = M * se

    # --- Total N and design effect ------------------------------------
    total_n = n_level4 * n_level3 * n_level2 * cluster_size

    # Approximate design effect with four levels of clustering
    design_effect = (
        1.0
        + (cluster_size - 1) * icc2
        + (cluster_size * n_level2 - 1) * icc3
        + (cluster_size * n_level2 * n_level3 - 1) * icc4
    )
    effective_n = total_n / design_effect

    # --- Outcome scaling ----------------------------------------------
    mdes_pct_points: Optional[float] = None
    mdes_raw: Optional[float] = None

    if outcome_type == "binary" and baseline_prob is not None:
        sigma_binary = math.sqrt(baseline_prob * (1.0 - baseline_prob))
        mdes_pct_points = mdes * sigma_binary * 100.0

    if outcome_type == "continuous" and outcome_sd is not None:
        mdes_raw = mdes * outcome_sd

    # --- Interpretation placeholder -----------------------------------
    interpretation = None

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=round(design_effect, 3),
        effective_n=round(effective_n, 1),
        total_n=total_n,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_raw=round(mdes_raw, 4) if mdes_raw else None,
        interpretation=interpretation,
    )
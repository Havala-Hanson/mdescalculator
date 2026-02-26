"""
Three-level Cluster Randomised Trial MDES engines.

Supported designs
-----------------
CRA3_3  – Complete random assignment at level 3 (e.g., districts randomised).
BCRA3_2 – Blocked CRT at level 2, level 3 as blocks (e.g., schools randomised
          within districts).

Notation
--------
K   = number of level-3 units (e.g., districts)
J   = number of level-2 units per level-3 unit (e.g., schools per district)
n   = number of level-1 units per level-2 unit (e.g., students per school)
ρ₃  = ICC at level 3
ρ₂  = ICC at level 2
R²₃ = R² at level 3 from covariates
R²₂ = R² at level 2 from covariates
R²₁ = R² at level 1 from covariates
P   = proportion of units assigned to treatment

CRA3_3 formula (Dong & Maynard, 2013)
--------------------------------------
σ_δ = sqrt[
        ρ₃(1 − R²₃) / (P(1−P)·K)
      + ρ₂(1 − R²₂) / (P(1−P)·K·J)
      + (1 − ρ₃ − ρ₂)(1 − R²₁) / (P(1−P)·K·J·n)
    ]
df  = K − 2

BCRA3_2 formula (Dong & Maynard, 2013)
---------------------------------------
Level-3 units serve as blocks (fixed effects); their variance is removed.
σ_δ = sqrt[
        ρ₂(1 − R²₂) / (P(1−P)·K·J)
      + (1 − ρ₃ − ρ₂)(1 − R²₁) / (P(1−P)·K·J·n)
    ]
df  = K·(J − 2)

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

from .mdes_two_level import MDESResult, _interpret_mdes, _multiplier


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
    """Compute σ_δ for the CRA3_3 design.

    Parameters
    ----------
    icc3:
        ICC at level 3 (ρ₃).
    icc2:
        ICC at level 2 (ρ₂).
    r2_level1, r2_level2, r2_level3:
        R² at each level from covariates.
    p_treat:
        Proportion assigned to treatment.
    n_level3:
        Number of level-3 units (K).
    n_level2:
        Number of level-2 units per level-3 unit (J).
    cluster_size:
        Number of level-1 units per level-2 unit (n).

    Returns
    -------
    float
        σ_δ.
    """
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
    """Compute the MDES for a three-level CRT randomised at level 3 (CRA3_3).

    Parameters
    ----------
    n_level3:
        Number of level-3 units K (e.g., districts).  Must be ≥ 3.
    n_level2:
        Number of level-2 units per level-3 unit J (e.g., schools per
        district).  Must be ≥ 1.
    cluster_size:
        Average number of level-1 units per level-2 unit n (e.g., students
        per school).  Must be ≥ 1.
    icc3:
        Intraclass correlation at level 3 (ρ₃ ∈ [0, 1)).
    icc2:
        Intraclass correlation at level 2 (ρ₂ ∈ [0, 1)).
        Note: ρ₂ + ρ₃ must be < 1.
    r2_level1, r2_level2, r2_level3:
        R² at each level from covariates (default 0).
    p_treat:
        Proportion of level-3 units assigned to treatment.  Defaults to 0.5.
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
        If inputs are outside valid ranges.
    """
    # ── Validation ────────────────────────────────────────────────────────
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

    # ── Calculation ───────────────────────────────────────────────────────
    df = n_level3 - 2
    se = _se_cra3_3(
        icc3, icc2, r2_level1, r2_level2, r2_level3,
        p_treat, n_level3, n_level2, cluster_size,
    )
    M = _multiplier(alpha, power, df)
    mdes = M * se

    total_n = n_level3 * n_level2 * cluster_size
    # Design effect accounts for two levels of clustering
    design_effect = (
        1.0
        + (cluster_size - 1) * icc2
        + (cluster_size * n_level2 - 1) * icc3
    )
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
    """Compute σ_δ for the BCRA3_2 design.

    Level-3 variance is absorbed by blocking (fixed level-3 effects),
    so it does not appear in the numerator of the first term.

    Parameters
    ----------
    icc3:
        ICC at level 3 (used only to determine within-block level-1 variance).
    icc2:
        ICC at level 2 (ρ₂).
    r2_level1, r2_level2:
        R² at levels 1 and 2 from covariates.
    p_treat:
        Proportion of level-2 units assigned to treatment within each block.
    n_level3:
        Number of level-3 units / blocks (K).
    n_level2:
        Number of level-2 units per level-3 unit (J).
    cluster_size:
        Number of level-1 units per level-2 unit (n).

    Returns
    -------
    float
        σ_δ.
    """
    denom_base = p_treat * (1.0 - p_treat)
    icc1 = max(0.0, 1.0 - icc3 - icc2)

    # Level-3 variance absorbed by blocking → not in first term
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
    """Compute the MDES for a three-level blocked CRT (BCRA3_2).

    Level-3 units (e.g., districts) serve as blocks.  Level-2 units
    (e.g., schools) are randomly assigned to treatment within each block.

    Parameters
    ----------
    n_level3:
        Number of level-3 blocks K.  Must be ≥ 1.
    n_level2:
        Number of level-2 units per block J.  Must be ≥ 3.
    cluster_size:
        Average number of level-1 units per level-2 unit n.  Must be ≥ 1.
    icc3:
        ICC at level 3 (ρ₃ ∈ [0, 1)).
    icc2:
        ICC at level 2 (ρ₂ ∈ [0, 1)).  ρ₂ + ρ₃ must be < 1.
    r2_level1, r2_level2:
        R² at levels 1 and 2 from covariates.
    p_treat:
        Proportion of level-2 units per block assigned to treatment.
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
        If inputs are outside valid ranges.
    """
    # ── Validation ────────────────────────────────────────────────────────
    if n_level3 < 1:
        raise ValueError("n_level3 must be at least 1.")
    if n_level2 < 3:
        raise ValueError(
            "n_level2 must be at least 3 (need ≥ 1 treatment and ≥ 1 control "
            "cluster per block, plus ≥1 df)."
        )
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

    # ── Calculation ───────────────────────────────────────────────────────
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

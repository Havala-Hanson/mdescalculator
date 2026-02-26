"""
Two-level Cluster Randomized Trial (CRT) MDES engine.

Design: CRA2_2
--------------
Clusters (level-2 units, e.g., schools or classrooms) are randomly assigned
to treatment or control.  Individual participants (level-1 units, e.g.,
students) are nested within clusters.

Formula (Bloom et al., 2007; Dong & Maynard, 2013 / PowerUp!)
--------------------------------------------------------------
MDES = M(α, power, df) × σ_δ

where
    σ_δ = sqrt[ ρ(1 - R²₂) / (P(1-P)·J)
              + (1 - ρ)(1 - R²₁) / (P(1-P)·J·n) ]

    M   = t_{1-α/2, df}  +  t_{power, df}   (multiplier)
    ρ   = intraclass correlation (ICC) at level 2
    R²₂ = proportion of level-2 variance explained by cluster-level covariates
    R²₁ = proportion of level-1 variance explained by individual covariates
    P   = proportion of clusters assigned to treatment
    J   = total number of clusters
    n   = average cluster (level-2) size
    df  = J − 2

Design effect and effective sample size
----------------------------------------
DEFF = 1 + (n − 1) · ρ
ESS  = J · n / DEFF

References
----------
Bloom, H. S., Richburg-Hayes, L., & Black, A. R. (2007). Using covariates to
improve precision for studies that randomize schools to evaluate educational
interventions. Educational Evaluation and Policy Analysis, 29(1), 30–59.

Dong, N., & Maynard, R. A. (2013). PowerUp!: A tool for calculating minimum
detectable effect sizes and minimum required sample sizes for experimental and
quasi-experimental design studies. Journal of Research on Educational
Effectiveness, 6(1), 24–67.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy import stats


@dataclass
class MDESResult:
    """Container for MDES calculation outputs."""

    mdes: float
    """Standardised minimum detectable effect size (Cohen's d)."""

    se: float
    """Standard error of the effect-size estimator."""

    df: int
    """Degrees of freedom used for the critical-value look-up."""

    design_effect: float
    """Design effect (DEFF = 1 + (n-1)·ρ)."""

    effective_n: float
    """Effective sample size = J·n / DEFF."""

    total_n: int
    """Total sample size = J · n."""

    mdes_pct_points: Optional[float] = None
    """MDES in percentage points (binary outcomes only)."""

    mdes_raw: Optional[float] = None
    """MDES in raw units if outcome_sd is provided."""

    interpretation: str = ""
    """Short plain-language interpretation of the MDES."""


def _multiplier(alpha: float, power: float, df: int) -> float:
    """Compute the MDES multiplier M = t_{1-α/2, df} + t_{power, df}.

    Parameters
    ----------
    alpha:
        Two-sided significance level (e.g., 0.05).
    power:
        Desired statistical power (e.g., 0.80).
    df:
        Degrees of freedom.

    Returns
    -------
    float
        The critical-value multiplier M.
    """
    # Guard against extreme df values
    effective_df = max(df, 1)
    t_alpha = stats.t.ppf(1.0 - alpha / 2.0, effective_df)
    t_power = stats.t.ppf(power, effective_df)
    return float(t_alpha + t_power)


def _se_cra2_2(
    icc: float,
    r2_level1: float,
    r2_level2: float,
    p_treat: float,
    n_clusters: int,
    cluster_size: int,
) -> float:
    """Compute σ_δ for the CRA2_2 design.

    Parameters
    ----------
    icc:
        Intraclass correlation (ρ) at level 2.
    r2_level1:
        Proportion of level-1 variance explained by covariates (R²₁).
    r2_level2:
        Proportion of level-2 variance explained by covariates (R²₂).
    p_treat:
        Proportion of clusters assigned to treatment (P).
    n_clusters:
        Total number of clusters (J).
    cluster_size:
        Average number of individuals per cluster (n).

    Returns
    -------
    float
        σ_δ (standard error of the effect-size estimator).
    """
    variance = (
        icc * (1.0 - r2_level2) / (p_treat * (1.0 - p_treat) * n_clusters)
        + (1.0 - icc) * (1.0 - r2_level1)
        / (p_treat * (1.0 - p_treat) * n_clusters * cluster_size)
    )
    return math.sqrt(max(variance, 0.0))


def compute_mdes_cra2_2(
    n_clusters: int,
    cluster_size: int,
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
    """Compute the MDES for a two-level cluster randomised trial (CRA2_2).

    Parameters
    ----------
    n_clusters:
        Total number of clusters (J).  Must be ≥ 3.
    cluster_size:
        Average number of individuals per cluster (n).  Must be ≥ 1.
    icc:
        Intraclass correlation coefficient ρ ∈ [0, 1).
    r2_level1:
        Proportion of individual-level variance explained by covariates
        (R²₁ ∈ [0, 1)).  Defaults to 0 (no covariates).
    r2_level2:
        Proportion of cluster-level variance explained by covariates
        (R²₂ ∈ [0, 1)).  Defaults to 0 (no covariates).
    p_treat:
        Proportion of clusters randomised to treatment (P ∈ (0, 1)).
        Defaults to 0.5 (equal allocation).
    alpha:
        Two-sided significance level.  Defaults to 0.05.
    power:
        Desired statistical power.  Defaults to 0.80.
    outcome_type:
        ``"continuous"`` or ``"binary"``.
    baseline_prob:
        Baseline event probability p₀ (required when outcome_type="binary").
    outcome_sd:
        Outcome standard deviation in raw units (optional; used only to
        report MDES in raw units for continuous outcomes).

    Returns
    -------
    MDESResult
        Dataclass containing MDES and related statistics.

    Raises
    ------
    ValueError
        If inputs are outside valid ranges.
    """
    # ── Input validation ──────────────────────────────────────────────────
    if n_clusters < 3:
        raise ValueError("n_clusters must be at least 3.")
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
            raise ValueError(
                "baseline_prob is required for binary outcomes."
            )
        if not 0.0 < baseline_prob < 1.0:
            raise ValueError("baseline_prob must be in (0, 1).")

    # ── Core calculation ──────────────────────────────────────────────────
    df = n_clusters - 2
    se = _se_cra2_2(icc, r2_level1, r2_level2, p_treat, n_clusters, cluster_size)
    M = _multiplier(alpha, power, df)
    mdes = M * se

    # ── Derived quantities ────────────────────────────────────────────────
    total_n = n_clusters * cluster_size
    design_effect = 1.0 + (cluster_size - 1) * icc
    effective_n = total_n / design_effect

    mdes_pct_points: Optional[float] = None
    mdes_raw: Optional[float] = None

    if outcome_type == "binary" and baseline_prob is not None:
        # Convert standardised MDES to percentage-point MDES
        sigma_binary = math.sqrt(baseline_prob * (1.0 - baseline_prob))
        mdes_pct_points = mdes * sigma_binary * 100.0

    if outcome_type == "continuous" and outcome_sd is not None:
        mdes_raw = mdes * outcome_sd

    interpretation = _interpret_mdes(mdes)

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
        interpretation=interpretation,
    )


def mdes_vs_clusters(
    cluster_sizes: list[int],
    n_clusters_range: range,
    icc: float,
    r2_level1: float = 0.0,
    r2_level2: float = 0.0,
    p_treat: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.80,
) -> dict[int, list[float]]:
    """Compute MDES over a range of cluster counts for multiple cluster sizes.

    Useful for generating visualisations showing how MDES changes with
    sample size.

    Parameters
    ----------
    cluster_sizes:
        List of cluster sizes to compute curves for.
    n_clusters_range:
        Range of cluster counts (J) to sweep over.
    icc, r2_level1, r2_level2, p_treat, alpha, power:
        As per :func:`compute_mdes_cra2_2`.

    Returns
    -------
    dict[int, list[float]]
        Mapping from cluster_size → list of MDES values, one per J in range.
    """
    results: dict[int, list[float]] = {}
    for cs in cluster_sizes:
        mdes_values = []
        for j in n_clusters_range:
            if j < 3:
                mdes_values.append(float("nan"))
                continue
            try:
                r = compute_mdes_cra2_2(
                    n_clusters=j,
                    cluster_size=cs,
                    icc=icc,
                    r2_level1=r2_level1,
                    r2_level2=r2_level2,
                    p_treat=p_treat,
                    alpha=alpha,
                    power=power,
                )
                mdes_values.append(r.mdes)
            except ValueError:
                mdes_values.append(float("nan"))
        results[cs] = mdes_values
    return results


def _interpret_mdes(mdes: float) -> str:
    """Return a plain-language interpretation of a standardised MDES value.

    Uses conventional Cohen's d benchmarks (Cohen, 1988).

    Parameters
    ----------
    mdes:
        Standardised effect size.

    Returns
    -------
    str
        Short interpretation string.
    """
    if mdes <= 0.20:
        label = "small"
    elif mdes <= 0.50:
        label = "small-to-medium"
    elif mdes <= 0.80:
        label = "medium-to-large"
    else:
        label = "large"

    return (
        f"Your study can detect a {label} effect (d ≈ {mdes:.2f}).  "
        "Using covariates or increasing your sample size will lower the MDES."
    )

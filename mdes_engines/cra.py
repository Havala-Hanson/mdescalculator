# mdes_engines/cra.py

import math
from scipy import stats
from mdes_engines.mdes_two_level import MDESResult


def compute_mdes_cra(
    n_clusters: int,
    cluster_size: int,
    icc: float,
    r2_level1: float,
    r2_level2: float,
    p_treat: float,
    alpha: float,
    power: float,
    outcome_type: str,
    baseline_prob: float,
    outcome_sd: float,
) -> MDESResult:
    """
    Modern CRA MDES engine (2-level cluster randomized trial).
    Implements Bloom (2007) / Dong & Maynard (2013).
    """

    # Degrees of freedom
    df = n_clusters - 2
    if df <= 1:
        raise ValueError("Not enough clusters for valid degrees of freedom.")

    # Outcome SD
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # M multiplier
    t_alpha = stats.t.ppf(1 - alpha / 2, df)
    t_power = stats.t.ppf(power, df)
    M = t_alpha + t_power

    # Variance components
    term_between = icc * (1 - r2_level2) / (p_treat * (1 - p_treat) * n_clusters)
    term_within = (1 - icc) * (1 - r2_level1) / (
        p_treat * (1 - p_treat) * n_clusters * cluster_size
    )

    var_delta = term_between + term_within
    se = math.sqrt(var_delta)

    # MDES (standardized)
    mdes = M * se

    # Raw-unit MDES (if continuous)
    mdes_raw = mdes * sd if outcome_type == "continuous" else None

    # Percentage-point MDES (if binary)
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # Design effect
    design_effect = 1 + (cluster_size - 1) * icc

    # Effective N
    total_n = n_clusters * cluster_size
    effective_n = total_n / design_effect

    # Interpretation
    if mdes < 0.10:
        interpretation = "Detects very small effects."
    elif mdes < 0.20:
        interpretation = "Detects small effects."
    elif mdes < 0.40:
        interpretation = "Detects moderate effects."
    else:
        interpretation = "Detects large effects."

    return MDESResult(
        mdes=mdes,
        se=se,
        df=df,
        design_effect=design_effect,
        effective_n=effective_n,
        total_n=total_n,
        mdes_raw=mdes_raw,
        mdes_pct_points=mdes_pct_points,
        interpretation=interpretation,
    )
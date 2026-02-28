"""
Shared utilities for two-level clustered designs.

This module intentionally contains only shared utilities that are not specific to a single design, to avoid:
- MDESResult (shared return object for all engines)
- _multiplier (critical-value helper)
- _interpret_mdes (shared interpretation helper)
- mdes_vs_clusters (visualization helper for CRA designs)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Dict, List

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------
# Shared return object for all MDES engines
# ---------------------------------------------------------------------

@dataclass
class MDESResult:
    mdes: float
    se: float
    df: int
    design_effect: float
    effective_n: float
    total_n: int
    mdes_pct_points: Optional[float] = None
    mdes_raw: Optional[float] = None
    interpretation: str = ""


# ---------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------

def _multiplier(alpha: float, power: float, df: int) -> float:
    """Compute M = t_{1-α/2, df} + t_{power, df}."""
    effective_df = max(df, 1)
    t_alpha = stats.t.ppf(1.0 - alpha / 2.0, effective_df)
    t_power = stats.t.ppf(power, effective_df)
    return float(t_alpha + t_power)


def _interpret_mdes(mdes: float) -> str:
    """Plain-language interpretation of standardized MDES."""
    if mdes <= 0.20:
        label = "small"
    elif mdes <= 0.50:
        label = "small-to-medium"
    elif mdes <= 0.80:
        label = "medium-to-large"
    else:
        label = "large"

    return (
        f"Your study can detect a {label} effect (d ≈ {mdes:.2f}). "
        "Using covariates or increasing your sample size will lower the MDES."
    )


# ---------------------------------------------------------------------
# Visualization helper (updated to use new CRA engine)
# ---------------------------------------------------------------------

def mdes_vs_clusters(
    cluster_sizes: List[int],
    n_clusters_range: range,
    icc: float,
    r2_level1: float = 0.0,
    r2_level2: float = 0.0,
    p_treat: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.80,
) -> Dict[int, List[float]]:
    """
    Compute MDES curves over a range of cluster counts for multiple cluster sizes.

    This function now uses the new family-level CRA engine:
        compute_mdes_cra
    """

    # Import here to avoid circular dependency
    from mdes_engines.cra import compute_mdes_cra

    results: Dict[int, List[float]] = {}

    for cs in cluster_sizes:
        mdes_values = []
        for j in n_clusters_range:
            if j < 3:
                mdes_values.append(float("nan"))
                continue

            try:
                r = compute_mdes_cra(
                    n_clusters=j,
                    cluster_size=cs,
                    icc=icc,
                    r2_level1=r2_level1,
                    r2_level2=r2_level2,
                    p_treat=p_treat,
                    alpha=alpha,
                    power=power,
                    outcome_type="continuous",
                    baseline_prob=None,
                    outcome_sd=None,
                )
                mdes_values.append(r.mdes)
            except ValueError:
                mdes_values.append(float("nan"))

        results[cs] = mdes_values

    return results
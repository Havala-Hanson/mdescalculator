# mdes_engines/ira.py

import math
from scipy import stats
from mdes_engines.mdes_two_level import MDESResult, _multiplier, _interpret_mdes


def compute_mdes_ira(
    n_individuals: int,
    p_treat: float,
    r2_level1: float,
    alpha: float,
    power: float,
    outcome_type: str,
    baseline_prob: float,
    outcome_sd: float,
) -> MDESResult:
    """
    Minimum detectable effect size for Individual Random Assignment (IRA).

    Model:
        Y_i = β0 + δ T_i + e_i

    MDES formula:
        MDES = M * sqrt( (1 - R²) / (P(1-P) * N) )

    where:
        M = t_{1-α/2, df} + t_{power, df}
        df = N - 2
    """

    # --- Validation ----------------------------------------------------
    if n_individuals < 10:
        raise ValueError("n_individuals must be at least 10.")
    if not 0 < p_treat < 1:
        raise ValueError("p_treat must be in (0, 1).")
    if not 0 <= r2_level1 < 1:
        raise ValueError("r2_level1 must be in [0, 1).")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1).")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1).")

    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        if not 0 < baseline_prob < 1:
            raise ValueError("baseline_prob must be in (0, 1).")

    # --- Degrees of freedom -------------------------------------------
    df = n_individuals - 2
    if df <= 1:
        raise ValueError("Not enough individuals for valid degrees of freedom.")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df)

    # --- Variance of effect estimator ---------------------------------
    var_delta = (1 - r2_level1) / (p_treat * (1 - p_treat) * n_individuals)
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Raw-unit MDES (continuous) -----------------------------------
    mdes_raw = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # --- Design effect & effective N ----------------------------------
    # For IRA, DEFF = 1 (no clustering)
    design_effect = 1.0
    total_n = n_individuals
    effective_n = n_individuals

    # --- Interpretation ------------------------------------------------
    interpretation = _interpret_mdes(mdes)

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=design_effect,
        effective_n=effective_n,
        total_n=total_n,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_raw=round(mdes_raw, 4) if mdes_raw else None,
        interpretation=interpretation,
    )
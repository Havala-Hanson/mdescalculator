# mdes_engines/its.py

import math
from mdes_engines.mdes_two_level import MDESResult, _multiplier, _interpret_mdes


def compute_mdes_its(
    n_timepoints_pre: int,
    n_timepoints_post: int,
    autocorrelation: float,
    alpha: float,
    power: float,
    outcome_type: str,
    baseline_prob: float,
    outcome_sd: float,
) -> MDESResult:
    """
    Minimum detectable effect size for a single-series Interrupted Time Series (ITS)
    with a level change at intervention and AR(1) errors.

    Approximate variance for the level-change estimator:

        Var(delta) ≈ (sigma^2 / N_eff)

    where N_eff is an effective number of independent timepoints that
    accounts for AR(1) autocorrelation.
    """

    # --- Validation ----------------------------------------------------
    if n_timepoints_pre < 3 or n_timepoints_post < 3:
        raise ValueError("At least 3 pre and 3 post timepoints are recommended.")
    if not -0.99 < autocorrelation < 0.99:
        raise ValueError("autocorrelation must be between -0.99 and 0.99.")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1).")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1).")

    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        if not 0 < baseline_prob < 1:
            raise ValueError("baseline_prob must be in (0, 1).")

    # --- Total timepoints ---------------------------------------------
    T = n_timepoints_pre + n_timepoints_post

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- Effective N under AR(1) --------------------------------------
    # Simple approximation: N_eff = T * (1 - phi) / (1 + phi)
    phi = autocorrelation
    if abs(phi) < 1e-6:
        n_eff = float(T)
    else:
        n_eff = T * (1 - phi) / (1 + phi)

    if n_eff <= 5:
        raise ValueError("Effective number of independent timepoints is too small.")

    # --- Degrees of freedom (approximate) ------------------------------
    df = int(round(n_eff)) - 2
    if df <= 1:
        raise ValueError("Not enough effective timepoints for valid degrees of freedom.")

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df)

    # --- Variance of level-change estimator ---------------------------
    # Approximate: Var(delta) ≈ sigma^2 / N_eff  (standardized sigma^2 = 1)
    var_delta = 1.0 / n_eff
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Raw-unit MDES (continuous) -----------------------------------
    mdes_raw = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # --- Design effect & effective N ----------------------------------
    # Single series; DEFF = 1, but we report effective N as N_eff
    design_effect = 1.0
    total_n = T
    effective_n = n_eff

    # --- Interpretation ------------------------------------------------
    interpretation = _interpret_mdes(mdes)

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=design_effect,
        effective_n=round(effective_n, 1),
        total_n=total_n,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_raw=round(mdes_raw, 4) if mdes_raw else None,
        interpretation=interpretation,
    )
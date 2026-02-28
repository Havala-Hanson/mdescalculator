# mdes_engines/rd.py

import math
from mdes_engines.mdes_two_level import MDESResult, _multiplier, _interpret_mdes


def compute_mdes_rd(
    n_units: int,
    bandwidth: float,
    running_var_sd: float,
    alpha: float,
    power: float,
    outcome_type: str,
    baseline_prob: float,
    outcome_sd: float,
) -> MDESResult:
    """
    Minimum detectable effect size for a simple sharp RD design.

    Assumes:
      - Single cutoff
      - Symmetric bandwidth around cutoff
      - Global linear specification
      - Equal variance on both sides

    Approximate MDES:
        MDES = M * sqrt( 1 / N_eff )

    where:
        N_eff = N * (bandwidth / running_var_sd)
        M     = t_{1-α/2, df} + t_{power, df}
        df    = N_eff - 2  (approximate)
    """

    # --- Validation ----------------------------------------------------
    if n_units < 20:
        raise ValueError("n_units must be at least 20.")
    if bandwidth <= 0:
        raise ValueError("bandwidth must be > 0.")
    if running_var_sd <= 0:
        raise ValueError("running_var_sd must be > 0.")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1).")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1).")

    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        if not 0 < baseline_prob < 1:
            raise ValueError("baseline_prob must be in (0, 1).")

    # --- Effective N near cutoff --------------------------------------
    # Fraction of sample inside bandwidth, assuming normal running variable
    frac_in_band = bandwidth / running_var_sd
    # Cap at 1.0 to avoid nonsense if bandwidth > SD
    frac_in_band = min(max(frac_in_band, 0.0), 1.0)

    n_eff = n_units * frac_in_band
    if n_eff <= 5:
        raise ValueError("Effective sample size near cutoff is too small.")

    # --- Degrees of freedom (approximate) ------------------------------
    df = int(round(n_eff)) - 2
    if df <= 1:
        raise ValueError("Not enough effective units for valid degrees of freedom.")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df)

    # --- Variance of effect estimator ---------------------------------
    var_delta = 1.0 / n_eff
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Raw-unit MDES (continuous) -----------------------------------
    mdes_raw = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # --- Design effect & effective N ----------------------------------
    # No clustering; DEFF = 1
    design_effect = 1.0
    total_n = n_units
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
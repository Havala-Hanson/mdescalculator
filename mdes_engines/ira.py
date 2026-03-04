import math
from mdes_engines.mdes_two_level import MDESResult, _multiplier


def compute_mdes_ira(
    n_individuals: int,
    two_tailed: bool,
    r2_level1: float,
    p: float = 0.5,
    g1: int = 0,
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
) -> MDESResult:
    """
    Minimum detectable effect size for Individual Random Assignment (IRA).

    Model:
        Y_i = β0 + δ T_i + e_i

    MDES formula:
        MDES = M * sqrt( (1 - R²) / (p(1-p) * N) )
        df = N - g1 - 2

    Parameters
    ----------
    p   : treatment proportion (default 0.5)
    g1  : number of covariates for df adjustment (default 0)
    """

    # --- Validation ----------------------------------------------------
    if n_individuals < 4:
        raise ValueError("n_individuals must be at least 4.")
    if not 0 <= r2_level1 < 1:
        raise ValueError("r2_level1 must be in [0, 1).")
    if not 0 < p < 1:
        raise ValueError("p must be in (0, 1).")
    if g1 < 0:
        raise ValueError("g1 must be >= 0.")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1).")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1).")

    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        bp = float(baseline_prob)
        if not 0 < bp < 1:
            raise ValueError("baseline_prob must be in (0, 1).")
    
    # --- One or two-tailed test ------------------------------------------------
    M = _multiplier(alpha, power, n_individuals - g1 - 2, two_tailed=two_tailed)
    
    # --- Degrees of freedom -------------------------------------------
    df = n_individuals - g1 - 2
    if df <= 1:
        raise ValueError("Not enough individuals for valid degrees of freedom (N - g1 - 2 must be > 1).")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(bp * (1 - bp))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- Variance of effect estimator ---------------------------------
    var_delta = (1 - r2_level1) / (p * (1 - p) * n_individuals)
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Raw-unit MDES (continuous) -----------------------------------
    mdes_raw = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # --- Design effect & effective N ----------------------------------
    design_effect = 1.0
    total_n = n_individuals
    effective_n = n_individuals

    # --- Interpretation placeholder -----------------------------------
    # Interpretation is now handled in services/interpretation.py
    interpretation = None

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=design_effect,
        effective_n=effective_n,
        total_n=total_n,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_raw=round(mdes_raw, 4) if mdes_raw else None,
        interpretation=interpretation if interpretation is not None else "",
    )
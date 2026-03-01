import math
from mdes_engines.mdes_two_level import MDESResult, _multiplier


def compute_mdes_bira(
    n_individuals: int,
    n_blocks: int,
    r2_level1: float,
    r2_level2: float,
    r2_level3: float | None = None,
    r2_level4: float | None = None,
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
) -> MDESResult:
    """
    Minimum detectable effect size for Blocked Individual Random Assignment (BIRA).

    Model:
        Y_ib = β0 + δ T_ib + γ_b + e_ib

    Base IRA variance:
        Var(delta) = (1 - R1^2) / [P(1-P) * N]

    Blocked IRA adjustment:
        Var_BIRA = Var_IRA * (B / (B - 1))

    We assume 50/50 treatment allocation: P = 0.5.
    """

    # --- Validation ----------------------------------------------------
    if n_individuals < 4:
        raise ValueError("n_individuals must be at least 4.")
    if n_blocks < 2:
        raise ValueError("n_blocks must be at least 2.")
    if not 0 <= r2_level1 < 1:
        raise ValueError("r2_level1 must be in [0, 1).")
    if not 0 <= r2_level2 < 1:
        raise ValueError("r2_level2 must be in [0, 1).")
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
    df = n_blocks - 2
    if df <= 1:
        raise ValueError("Not enough blocks for valid degrees of freedom.")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df)

    # --- Variance of effect estimator ---------------------------------
    P = 0.5
    block_factor = n_blocks / (n_blocks - 1)

    var_ira = (1 - r2_level1) / (P * (1 - P) * n_individuals)
    var_delta = var_ira * block_factor
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
    effective_n = total_n

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
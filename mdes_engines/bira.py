# mdes_engines/bira.py

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
    two_tailed: bool = True,
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
    M = _multiplier(alpha, power, df, two_tailed=two_tailed)

    # --- Variance of effect estimator ---------------------------------
    P = 0.5
    block_factor = n_blocks / (n_blocks - 1)

    var_ira = (1 - r2_level1) / (P * (1 - P) * n_individuals)
    var_delta = var_ira * block_factor
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Standardized MDES (continuous) -----------------------------------
    mdes_standardized = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    if outcome_type == "binary":
        mdes_pct_points = mdes * sd * 100   # sd = sqrt(p0*(1-p0))
    else:
        mdes_pct_points = None

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
        mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
        interpretation=interpretation,
    )

def compute_mdes_bira2_1c(
    n_individuals: int,
    n_blocks: int,
    r2_level1: float = 0.0,
    alpha: float = 0.05,
    power: float = 0.80,
    two_tailed: bool = True,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
    prop_treated: float = 0.5,
    n_covariates_level1: int = 0,
) -> MDESResult:
    """
    BIRA2_1c: Two-level blocked IRA, constant block effect model
    (PowerUpR: mdes.bira2c1).

    Var(delta) = (1 - R1^2) / [p(1-p) * J * n]
    df = J*(n - 1) - g1 - 1
    """

    # --- Validation ---
    if n_blocks < 2:
        raise ValueError("n_blocks must be at least 2.")
    if n_individuals <= n_blocks:
        raise ValueError("n_individuals must exceed n_blocks.")
    if not 0 <= r2_level1 < 1:
        raise ValueError("r2_level1 must be in [0, 1).")
    if not 0 < prop_treated < 1:
        raise ValueError("prop_treated must be in (0, 1).")

    J = n_blocks
    N = n_individuals
    n = N / J
    P = prop_treated

    # --- Degrees of freedom ---
    df = J * (n - 1) - n_covariates_level1 - 1
    df = int(df)
    if df <= 1:
        raise ValueError("Not enough degrees of freedom for BIRA2_1c.")

    # --- Outcome SD ---
    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier ---
    M = _multiplier(alpha, power, df, two_tailed=two_tailed)

    # --- Variance ---
    var_delta = (1 - r2_level1) / (P * (1 - P) * J * n)
    se = math.sqrt(var_delta)

    # --- MDES ---
    mdes = M * se
    mdes_standardized = mdes * sd if outcome_type == "continuous" else None
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=1.0,
        effective_n=round(N, 1),
        total_n=N,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
        interpretation=None,
    )

def compute_mdes_bira2_1f(
    n_individuals: int,
    n_blocks: int,
    r2_level1: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_tailed: bool = True,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
) -> MDESResult:
    """
    BIRA2_1f: Two-level blocked IRA, fixed block effects.
    Thin wrapper around compute_mdes_bira.
    """
    return compute_mdes_bira(
        n_individuals=n_individuals,
        n_blocks=n_blocks,
        r2_level1=r2_level1,
        r2_level2=0.0,
        r2_level3=None,
        r2_level4=None,
        alpha=alpha,
        power=power,
        outcome_type=outcome_type,
        baseline_prob=baseline_prob,
        outcome_sd=outcome_sd,
        two_tailed=two_tailed,
    )

def compute_mdes_bira2_1r(
    n_individuals: int,
    n_blocks: int,
    icc2: float,
    omega2: float,
    r2_level1: float = 0.0,   # r21
    r2_level2: float = 0.0,   # r2t2
    alpha: float = 0.05,
    power: float = 0.80,
    two_tailed: bool = True,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
    prop_treated: float = 0.5,
    rel1: float = 1.0,
) -> MDESResult:
    """
    BIRA2_1r: Two-level blocked IRA, random block effects (PowerUpR: mdes.bira2r1).

    Var(delta) =
        icc2 * omega2 * (1 - r2_level2) / J
      + (1 - icc2) * (1 - r2_level1) / (p*(1-p)*J*n*rel1)

    df = J - 1
    """
    if n_individuals < 4:
        raise ValueError("n_individuals must be at least 4.")
    if n_blocks < 2:
        raise ValueError("n_blocks must be at least 2.")
    if not 0 <= icc2 < 1:
        raise ValueError("icc2 must be in [0, 1).")
    if not 0 <= r2_level1 < 1 or not 0 <= r2_level2 < 1:
        raise ValueError("R² values must be in [0, 1).")
    if not 0 < prop_treated < 1:
        raise ValueError("prop_treated must be in (0, 1).")

    J = n_blocks
    N = n_individuals
    n = N / J
    P = prop_treated

    df = J - 1
    if df <= 1:
        raise ValueError("Not enough blocks for valid degrees of freedom.")

    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    M = _multiplier(alpha, power, df, two_tailed=two_tailed)

    var_delta = (
        icc2 * omega2 * (1 - r2_level2) / J
        + (1 - icc2) * (1 - r2_level1) / (P * (1 - P) * J * n * rel1)
    )
    se = math.sqrt(var_delta)
    mdes = M * se

    mdes_standardized = mdes * sd if outcome_type == "continuous" else None
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=1.0,
        effective_n=round(N, 1),
        total_n=N,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
        interpretation=None,
    )

def compute_mdes_bira3_1r(
    n_blocks: int,                 # K
    n_clusters_per_block: int,     # J
    cluster_size: int,             # n
    icc2: float,                   # rho2
    icc3: float,                   # rho3
    omega2: float,
    omega3: float,
    r2_level1: float = 0.0,        # r21
    r2_level2: float = 0.0,        # r2t2
    r2_level3: float = 0.0,        # r2t3
    alpha: float = 0.05,
    power: float = 0.80,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
    prop_treated: float = 0.5,
    two_tailed: bool = True,
) -> MDESResult:
    """
    BIRA3_1r: Three-level blocked IRA, random block and cluster effects
    (PowerUpR: mdes.bira3r1).

    Var(delta) =
        icc3 * omega3 * (1 - r2_level3) / K
      + icc2 * omega2 * (1 - r2_level2) / (J*K)
      + (1 - icc3 - icc2) * (1 - r2_level1) / (p*(1-p)*J*K*n)

    df = K - 1
    """
    if n_blocks < 2:
        raise ValueError("n_blocks must be at least 2.")
    if n_clusters_per_block < 1 or cluster_size < 2:
        raise ValueError("n_clusters_per_block >=1 and cluster_size >=2 required.")
    if not 0 <= icc2 < 1 or not 0 <= icc3 < 1 or icc2 + icc3 >= 1:
        raise ValueError("icc2, icc3 in [0,1) and icc2+icc3 < 1.")
    for r2 in (r2_level1, r2_level2, r2_level3):
        if not 0 <= r2 < 1:
            raise ValueError("R² values must be in [0, 1).")
    if not 0 < prop_treated < 1:
        raise ValueError("prop_treated must be in (0, 1).")

    K = n_blocks
    J = n_clusters_per_block
    n = cluster_size
    N = K * J * n
    P = prop_treated

    df = K - 1
    if df <= 1:
        raise ValueError("Not enough blocks for valid degrees of freedom.")

    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    M = _multiplier(alpha, power, df, two_tailed=two_tailed)

    var_delta = (
        icc3 * omega3 * (1 - r2_level3) / K
        + icc2 * omega2 * (1 - r2_level2) / (J * K)
        + (1 - icc3 - icc2) * (1 - r2_level1) / (P * (1 - P) * J * K * n)
    )
    se = math.sqrt(var_delta)
    mdes = M * se

    mdes_standardized = mdes * sd if outcome_type == "continuous" else None
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=1.0,
        effective_n=round(N, 1),
        total_n=N,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
        interpretation=None,
    )

def compute_mdes_bira4_1r(
    n_blocks: int,                  # L
    n_sites_per_block: int,         # K
    n_clusters_per_site: int,       # J
    cluster_size: int,              # n
    icc2: float,                    # rho2
    icc3: float,                    # rho3
    icc4: float,                    # rho4
    omega2: float,
    omega3: float,
    omega4: float,
    r2_level1: float = 0.0,         # r21
    r2_level2: float = 0.0,         # r2t2
    r2_level3: float = 0.0,         # r2t3
    r2_level4: float = 0.0,         # r2t4
    alpha: float = 0.05,
    power: float = 0.80,
    two_tailed: bool = True,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
    prop_treated: float = 0.5,
) -> MDESResult:
    """
    BIRA4_1r: Four-level blocked IRA, random effects at levels 2–4
    (PowerUpR: mdes.bira4r1).

    Var(delta) =
        icc4 * omega4 * (1 - r2_level4) / L
      + icc3 * omega3 * (1 - r2_level3) / (K*L)
      + icc2 * omega2 * (1 - r2_level2) / (J*K*L)
      + (1 - icc4 - icc3 - icc2) * (1 - r2_level1) / (p*(1-p)*J*K*L*n)

    df = L - 1
    """
    if n_blocks < 2:
        raise ValueError("n_blocks (L) must be at least 2.")
    if n_sites_per_block < 1 or n_clusters_per_site < 1 or cluster_size < 2:
        raise ValueError("n_sites_per_block, n_clusters_per_site >=1 and cluster_size >=2 required.")
    if not 0 <= icc2 < 1 or not 0 <= icc3 < 1 or not 0 <= icc4 < 1:
        raise ValueError("ICC values must be in [0, 1).")
    if icc2 + icc3 + icc4 >= 1:
        raise ValueError("icc2 + icc3 + icc4 must be < 1.")
    for r2 in (r2_level1, r2_level2, r2_level3, r2_level4):
        if not 0 <= r2 < 1:
            raise ValueError("R² values must be in [0, 1).")
    if not 0 < prop_treated < 1:
        raise ValueError("prop_treated must be in (0, 1).")

    L = n_blocks
    K = n_sites_per_block
    J = n_clusters_per_site
    n = cluster_size
    N = L * K * J * n
    P = prop_treated

    df = L - 1
    if df <= 1:
        raise ValueError("Not enough blocks for valid degrees of freedom.")

    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    M = _multiplier(alpha, power, df, two_tailed=two_tailed)

    var_delta = (
        icc4 * omega4 * (1 - r2_level4) / L
        + icc3 * omega3 * (1 - r2_level3) / (K * L)
        + icc2 * omega2 * (1 - r2_level2) / (J * K * L)
        + (1 - icc4 - icc3 - icc2) * (1 - r2_level1)
          / (P * (1 - P) * J * K * L * n)
    )
    se = math.sqrt(var_delta)
    mdes = M * se

    mdes_standardized = mdes * sd if outcome_type == "continuous" else None
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=1.0,
        effective_n=round(N, 1),
        total_n=N,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
        interpretation=None,
    )
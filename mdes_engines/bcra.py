import math
from mdes_engines.mdes_two_level import MDESResult, _multiplier

def compute_mdes_bcra(
    n_clusters: int,
    cluster_size: int,
    n_blocks: int,
    icc: float,
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
    Minimum detectable effect size for Blocked Cluster Random Assignment (BCRA).

    Core variance structure (Dong & Maynard 2013):

        Var(delta) =
            [ ρ (1 - R2_2) / (P(1-P) * B) ] +
            [ (1 - ρ)(1 - R2_1) / (P(1-P) * B * n) ]

    with block adjustment:
            B / (B - 1)

    We assume equal allocation: P = 0.5.
    """

    # --- Validation ----------------------------------------------------
    if n_clusters < 4:
        raise ValueError("n_clusters must be at least 4.")
    if cluster_size < 1:
        raise ValueError("cluster_size must be at least 1.")
    if n_blocks < 2:
        raise ValueError("n_blocks must be at least 2.")
    if not 0 <= icc < 1:
        raise ValueError("icc must be in [0, 1).")
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

    # --- Variance components ------------------------------------------
    B = n_blocks
    J = n_clusters
    n = cluster_size
    rho = icc
    P = 0.5

    term_between = rho * (1 - r2_level2) / (P * (1 - P) * B)
    term_within = (1 - rho) * (1 - r2_level1) / (P * (1 - P) * B * n)

    var_cra = term_between + term_within

    # Block adjustment
    block_factor = B / (B - 1)

    var_delta = var_cra * block_factor
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Standardized MDES (continuous) -----------------------------------
    mdes_standardized = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # --- Design effect & effective N ----------------------------------
    design_effect = 1 + (cluster_size - 1) * icc
    total_n = n_clusters * cluster_size
    effective_n = total_n / design_effect

    # --- Interpretation placeholder -----------------------------------
    interpretation = None


    if outcome_type == "binary":
            return MDESResult(
            mdes=round(mdes, 4),
            se=round(se, 4),
            df=df,
            design_effect=round(design_effect, 3),
            effective_n=round(effective_n, 1),
            total_n=total_n,
            mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
            mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
            interpretation=interpretation,
        )
    else:
        return MDESResult(
            mdes=round(mdes, 4),
            se=round(se, 4),
            df=df,
            design_effect=round(design_effect, 3),
            effective_n=round(effective_n, 1),
            total_n=total_n,
            mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
            mdes_pct_points=None,
            interpretation=interpretation,
        )

def compute_mdes_bcra3_2f(
    n_level3: int,          # K blocks
    n_level2: int,          # J clusters per block
    cluster_size: int,      # n individuals per cluster
    icc2: float,            # level-2 ICC (clusters)
    r2_level1: float,
    r2_level2: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_tailed: bool = True,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
) -> MDESResult:
    """
    MDES for Blocked Cluster Random Assignment (BCRA3_2f):
    3-level CRT with clusters randomized within blocks, blocks treated as fixed effects.

    Structure:
        Level 3: blocks (fixed)
        Level 2: clusters (randomized)
        Level 1: individuals

    Variance (Dong & Maynard-style):

        Var(delta) =
            4 / (K * J) * [
                icc2 * (1 - R2_2)
              + (1 - icc2) * (1 - R2_1) / n
            ] * [ K / (K - 1) ]

    where:
        K = n_level3 (blocks)
        J = n_level2 (clusters per block)
        n = cluster_size
    """

    # --- Validation ----------------------------------------------------
    if n_level3 < 2:
        raise ValueError("n_level3 (blocks) must be at least 2.")
    if n_level2 < 2:
        raise ValueError("n_level2 (clusters per block) must be at least 2.")
    if cluster_size < 1:
        raise ValueError("cluster_size must be at least 1.")
    if not 0 <= icc2 < 1:
        raise ValueError("icc2 must be in [0, 1).")
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
    # df = K(J - 1) - 1
    K = n_level3
    J = n_level2
    df = K * (J - 1) - 1
    if df <= 1:
        raise ValueError("Not enough blocks/clusters for valid degrees of freedom.")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df, two_tailed=two_tailed)

    # --- Variance components ------------------------------------------
    n = cluster_size
    rho2 = icc2
    P = 0.5  # equal allocation

    # Effective number of randomized units = K * J
    # Base CRT variance (2-level within blocks)
    term_between = rho2 * (1 - r2_level2) / (P * (1 - P) * K * J)
    term_within = (1 - rho2) * (1 - r2_level1) / (P * (1 - P) * K * J * n)
    var_cra = term_between + term_within

    # Block adjustment for fixed effects at level 3
    block_factor = K / (K - 1)
    var_delta = var_cra * block_factor
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Standardized MDES (continuous) --------------------------------
    mdes_standardized = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # --- Design effect & effective N ----------------------------------
    total_n = K * J * n
    # For reporting, use standard 2-level DE at the cluster level
    design_effect = 1 + (n - 1) * icc2
    effective_n = total_n / design_effect

    # --- Interpretation placeholder -----------------------------------
    interpretation = None

    if outcome_type == "binary":
        return MDESResult(
            mdes=round(mdes, 4),
            se=round(se, 4),
            df=df,
            design_effect=round(design_effect, 3),
            effective_n=round(effective_n, 1),
            total_n=total_n,
            mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points is not None else None,
            mdes_standardized=round(mdes_standardized, 4) if mdes_standardized is not None else None,
            interpretation=interpretation,
        )
    else:
        return MDESResult(
            mdes=round(mdes, 4),
            se=round(se, 4),
            df=df,
            design_effect=round(design_effect, 3),
            effective_n=round(effective_n, 1),
            total_n=total_n,
            mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points is not None else None,
            interpretation=interpretation,
        )

def compute_mdes_bcra3_2r(
    n_level3: int,          # K blocks (random)
    n_level2: int,          # J clusters per block
    cluster_size: int,      # n individuals per cluster
    icc3: float,            # level-3 ICC (blocks)
    icc2: float,            # level-2 ICC (clusters)
    r2_level1: float,
    r2_level2: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_tailed: bool = True,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
) -> MDESResult:
    """
    MDES for Blocked Cluster Random Assignment (BCRA3_2r):
    3-level CRT with clusters randomized within blocks, blocks treated as random effects.

    Structure:
        Level 3: blocks (random)
        Level 2: clusters (randomized)
        Level 1: individuals

    Variance (Dong & Maynard-style):

        Var(delta) =
            4 * [
                icc3 * (1 - R2_3) / K
              + icc2 * (1 - R2_2) / (K * J)
              + (1 - icc2 - icc3) * (1 - R2_1) / (K * J * n)
            ]

    df = K - 2
    """

    # --- Validation ----------------------------------------------------
    if n_level3 < 4:
        raise ValueError("n_level3 (blocks) must be at least 4 for df = K - 2.")
    if n_level2 < 2:
        raise ValueError("n_level2 (clusters per block) must be at least 2.")
    if cluster_size < 1:
        raise ValueError("cluster_size must be at least 1.")
    if not 0 <= icc3 < 1:
        raise ValueError("icc3 must be in [0, 1).")
    if not 0 <= icc2 < 1:
        raise ValueError("icc2 must be in [0, 1).")
    if icc2 + icc3 >= 1:
        raise ValueError("icc2 + icc3 must be < 1.")
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
    K = n_level3
    J = n_level2
    n = cluster_size
    df = K - 2
    if df <= 1:
        raise ValueError("Not enough blocks for valid degrees of freedom.")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df, two_tailed=two_tailed)

    # --- Variance components ------------------------------------------
    P = 0.5  # equal allocation

    # Level-3 variance (blocks)
    term_l3 = icc3 * (1 - r2_level2) / (P * (1 - P) * K)

    # Level-2 variance (clusters)
    term_l2 = icc2 * (1 - r2_level2) / (P * (1 - P) * K * J)

    # Level-1 variance
    term_l1 = (1 - icc2 - icc3) * (1 - r2_level1) / (P * (1 - P) * K * J * n)

    var_delta = term_l3 + term_l2 + term_l1
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Standardized MDES (continuous) --------------------------------       
    mdes_standardized = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # --- Design effect & effective N ----------------------------------
    total_n = K * J * n
    design_effect = 1 + (n - 1) * icc2 + (J * n - 1) * icc3
    effective_n = total_n / design_effect

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=round(design_effect, 3),
        effective_n=round(effective_n, 1),
        total_n=total_n,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        mdes_standardized=round(mdes_standardized, 4) if mdes_standardized else None,
        interpretation="",
    )
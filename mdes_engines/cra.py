import math
from mdes_engines.mdes_two_level import MDESResult, _multiplier


def compute_mdes_cra(
    n_clusters: int,
    cluster_size: int,
    icc: float,
    r2_level1: float,
    r2_level2: float,
    p_treat: float = 0.5,
    rel1: float = 1.0,
    g2: int = 0,
    alpha: float = 0.05,
    power: float = 0.80,
    two_tailed: bool = True,
    outcome_type: str = "continuous",
    baseline_prob: float | None = None,
    outcome_sd: float | None = None,
) -> MDESResult:
    """
    MDES for two-level Cluster Random Assignment (CRA2_2r).

    Mirrors R's mdes.cra2r2 (PowerUpR / PowerUp!):

        df  = J - g2 - 2
        SSE = sqrt[
            ρ (1 - R²₂) / (p(1-p) J)
          + (1 - ρ) (1 - R²₁) / (p(1-p) J n · rel1)
        ]

    Parameters
    ----------
    p_treat  : treatment proportion (R: p, default 0.50)
    rel1     : outcome measurement reliability (R: rel1, default 1.0)
    g2       : number of level-2 covariates for df adjustment (R: g2, default 0)
    two_tailed: use two-tailed critical value (R: two.tailed, default True)

    For 3-level designs use compute_mdes_cra3_3; for 4-level use compute_mdes_cra4_4.
    """

    # --- Validation ----------------------------------------------------
    if n_clusters < 4:
        raise ValueError("n_clusters must be at least 4.")
    if cluster_size < 1:
        raise ValueError("cluster_size must be at least 1.")
    if not 0 <= icc < 1:
        raise ValueError("icc must be in [0, 1).")
    if not 0 <= r2_level1 < 1:
        raise ValueError("r2_level1 must be in [0, 1).")
    if not 0 <= r2_level2 < 1:
        raise ValueError("r2_level2 must be in [0, 1).")
    if not 0 < p_treat < 1:
        raise ValueError("p_treat must be in (0, 1).")
    if not 0 < rel1 <= 1:
        raise ValueError("rel1 must be in (0, 1].")
    if g2 < 0:
        raise ValueError("g2 must be >= 0.")
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
    df = n_clusters - g2 - 2
    if df <= 1:
        raise ValueError("Not enough clusters for valid degrees of freedom (J - g2 - 2 must be > 1).")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df, two_tailed=two_tailed)

    # --- Variance components ------------------------------------------
    J = n_clusters
    n = cluster_size
    rho = icc
    P = p_treat

    term_between = rho * (1 - r2_level2) / (P * (1 - P) * J)
    term_within = (1 - rho) * (1 - r2_level1) / (P * (1 - P) * J * n * rel1)

    var_delta = term_between + term_within
    se = math.sqrt(var_delta)

    # --- Standardized MDES --------------------------------------------
    mdes = M * se

    # --- Raw-unit MDES (continuous) -----------------------------------
    mdes_raw = mdes * sd if outcome_type == "continuous" else None

    # --- Percentage-point MDES (binary) -------------------------------
    mdes_pct_points = mdes * 100 if outcome_type == "binary" else None

    # --- Design effect & effective N ----------------------------------
    design_effect = 1 + (cluster_size - 1) * icc
    total_n = n_clusters * cluster_size
    effective_n = total_n / design_effect

    # --- Interpretation placeholder -----------------------------------
    interpretation = None

    return MDESResult(
        mdes=round(mdes, 4),
        se=round(se, 4),
        df=df,
        design_effect=round(design_effect, 3),
        effective_n=round(effective_n, 1),
        total_n=total_n,
        mdes_raw=round(mdes_raw, 4) if mdes_raw else None,
        mdes_pct_points=round(mdes_pct_points, 2) if mdes_pct_points else None,
        interpretation=interpretation,
    )
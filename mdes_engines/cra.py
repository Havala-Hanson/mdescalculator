import math
from mdes_engines.mdes_two_level import MDESResult, _multiplier


def compute_mdes_cra(
    n_clusters: int,
    cluster_size: int,
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
    MDES for Cluster Random Assignment (CRA), 2–4 level variants.

    Core 2-level formula (Bloom 2007 / Dong & Maynard 2013):

        Var(delta) = σ_y^2 * [
            ρ (1 - R2_2) / (P(1-P) J)
          + (1 - ρ) (1 - R2_1) / (P(1-P) J n)
        ]

    We assume 50/50 treatment allocation: P = 0.5.
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
    df = n_clusters - 2
    if df <= 1:
        raise ValueError("Not enough clusters for valid degrees of freedom.")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df)

    # --- Variance components ------------------------------------------
    J = n_clusters
    n = cluster_size
    rho = icc
    P = 0.5  # equal allocation

    term_between = rho * (1 - r2_level2) / (P * (1 - P) * J)
    term_within = (1 - rho) * (1 - r2_level1) / (P * (1 - P) * J * n)

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
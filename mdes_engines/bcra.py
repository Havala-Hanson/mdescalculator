# mdes_engines/bcra.py

import math
from mdes_engines.mdes_two_level import MDESResult, _multiplier, _interpret_mdes


def compute_mdes_bcra(
    n_clusters: int,
    cluster_size: int,
    n_blocks: int,
    icc: float,
    r2_level1: float,
    r2_level2: float,
    p_treat: float,
    alpha: float,
    power: float,
    outcome_type: str,
    baseline_prob: float,
    outcome_sd: float,
) -> MDESResult:
    """
    Minimum detectable effect size for Blocked Cluster Random Assignment (BCRA).

    Model:
        Y_ijb = β0 + δ T_jb + γ_b + u_jb + e_ijb

    MDES formula:
        MDES = M * sqrt( Var_delta ) * sqrt(B / (B - 1))

    where Var_delta is the CRA variance:
        Var_delta = ρ(1 - R²₂) / [P(1-P) J]
                    + (1 - ρ)(1 - R²₁) / [P(1-P) J n]

    and:
        M  = t_{1-α/2, df} + t_{power, df}
        df = J - B - 1   (clusters within blocks)
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
    if not 0 < p_treat < 1:
        raise ValueError("p_treat must be in (0, 1).")
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
    # Clusters within blocks: df ≈ J - B - 1
    df = n_clusters - n_blocks - 1
    if df <= 1:
        raise ValueError("Not enough clusters/blocks for valid degrees of freedom.")

    # --- Outcome SD ----------------------------------------------------
    if outcome_type == "binary":
        sd = math.sqrt(baseline_prob * (1 - baseline_prob))
    else:
        sd = outcome_sd if outcome_sd is not None else 1.0

    # --- M multiplier --------------------------------------------------
    M = _multiplier(alpha, power, df)

    # --- CRA variance component ---------------------------------------
    var_cra = (
        icc * (1 - r2_level2) / (p_treat * (1 - p_treat) * n_clusters)
        + (1 - icc) * (1 - r2_level1)
        / (p_treat * (1 - p_treat) * n_clusters * cluster_size)
    )

    # --- Block factor --------------------------------------------------
    block_factor = n_blocks / (n_blocks - 1)

    var_delta = var_cra * block_factor
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

    # --- Interpretation ------------------------------------------------
    interpretation = _interpret_mdes(mdes)

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
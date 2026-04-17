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
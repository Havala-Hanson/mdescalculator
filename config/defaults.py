DEFAULT_INPUTS = {

    # ─────────────────────────────────────────────────────────────
    # IRA — Individual Random Assignment
    # ─────────────────────────────────────────────────────────────
    "IRA": {
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "r2_level1": 0.0,
            "two_tailed": True,
        },
        "continuous": {
            "n_individuals": 200,
            "icc": 0.00,
            "effect_size": 0.20,
            "outcome_sd_input": 1.0,
        },
        "binary": {
            "n_individuals": 200,
            "icc": 0.00,
            "baseline_prob": 0.50,
            "effect_size": 0.20,
        },
    },

    # ─────────────────────────────────────────────────────────────
    # BIRA — Blocked Individual Random Assignment
    # ─────────────────────────────────────────────────────────────
    "BIRA": {
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "p_treat": 0.50,
            "p_block_treat": 0.50,
            "block_prop": 0.50,
            "n_blocks": 10,
            "r2_level1": 0.0,
            "r2_level2": 0.0,
        },
        "continuous": {
            "n_individuals": 200,
            "icc": 0.00,
            "effect_size": 0.20,
            "outcome_sd_input": 1.0,
        },
        "binary": {
            "n_individuals": 200,
            "icc": 0.00,
            "baseline_prob": 0.50,
            "effect_size": 0.20,
        },
    },

    # ─────────────────────────────────────────────────────────────
    # CRA — Simple Cluster Random Assignment
    # ─────────────────────────────────────────────────────────────
    "CRA": {
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "r2_level1": 0.0,
            "r2_level2": 0.0,
            "r2_level3": 0.0,   # needed for CRA3_3r
            "r2_level4": 0.0,   # needed for CRA4_4r
        },
        "continuous": {
            "n_clusters": 40,
            "cluster_size": 25,
            "icc": 0.10,
            "effect_size": 0.20,
            "outcome_sd_input": 1.0,
        },
        "binary": {
            "n_clusters": 40,
            "cluster_size": 25,
            "icc": 0.08,
            "baseline_prob": 0.50,
            "effect_size": 0.20,
        },
    },

    # ─────────────────────────────────────────────────────────────
    # BCRA — Blocked Cluster Random Assignment
    # ─────────────────────────────────────────────────────────────
    "BCRA": {
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "p_treat": 0.50,
            "p_block_treat": 0.50,
            "block_prop": 0.50,
            "n_blocks": 10,
            "r2_level1": 0.0,
            "r2_level2": 0.0,
            "r2_level3": 0.0,   # needed for 3-level BCRA
            "r2_level4": 0.0,   # needed for 4-level BCRA
        },
        "continuous": {
            "n_clusters": 40,
            "cluster_size": 25,
            "icc": 0.10,
            "effect_size": 0.20,
            "outcome_sd_input": 1.0,
        },
        "binary": {
            "n_clusters": 40,
            "cluster_size": 25,
            "icc": 0.08,
            "baseline_prob": 0.50,
            "effect_size": 0.20,
        },
    },

    # ─────────────────────────────────────────────────────────────
    # RD — Regression Discontinuity (individual or cluster)
    # ─────────────────────────────────────────────────────────────
    "RD": {
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "cutoff": 0.0,
            "kernel": "triangular",
            "treatment_side": "right",
            "r2_level1": 0.0,
            "r2_level2": 0.0,
            "r2_level3": 0.0,
        },
        "continuous": {
            "n_units": 2000,
            "bandwidth": 0.5,
            "running_var_sd": 1.0,
            "effect_size": 0.20,
            "outcome_sd_input": 1.0,
        },
        "binary": {
            "n_units": 2000,
            "bandwidth": 0.5,
            "running_var_sd": 1.0,
            "baseline_prob": 0.50,
            "effect_size": 0.20,
        },
    },

    # ─────────────────────────────────────────────────────────────
    # ITS — Interrupted Time Series (cluster-level)
    # ─────────────────────────────────────────────────────────────
    "ITS": {
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "r2_level1": 0.0,
            "r2_level2": 0.0,
        },
        "continuous": {
            "n_timepoints_pre": 12,
            "n_timepoints_post": 12,
            "autocorrelation": 0.40,
            "n_clusters": 20,
            "cluster_size": 30,
            "icc": 0.10,
            "effect_size": 0.20,
            "outcome_sd_input": 1.0,
        },
        "binary": {
            "n_timepoints_pre": 12,
            "n_timepoints_post": 12,
            "autocorrelation": 0.40,
            "n_clusters": 20,
            "cluster_size": 30,
            "icc": 0.10,
            "baseline_prob": 0.50,
            "effect_size": 0.20,
        },
    },
}
DEFAULT_INPUTS = {
    "IRA": {
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
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "r2_level1": 0.0,
            "r2_level2": 0.0,
        },
    },

    "CRA": {
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
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "r2_level1": 0.0,
            "r2_level2": 0.0,
        },
    },

    "BCRA": {
        "continuous": {
            "n_clusters": 40,
            "cluster_size": 25,
            "n_blocks": 10,
            "block_effect": "random",
            "icc": 0.10,
            "effect_size": 0.20,
            "outcome_sd_input": 1.0,
        },
        "binary": {
            "n_clusters": 40,
            "cluster_size": 25,
            "n_blocks": 10,
            "block_effect": "random",
            "icc": 0.08,
            "baseline_prob": 0.50,
            "effect_size": 0.20,
        },
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
            "r2_level1": 0.0,
            "r2_level2": 0.0,
        },
    },

    "RD": {
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
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
        },
    },

    "ITS": {
        "continuous": {
            "n_timepoints_pre": 12,
            "n_timepoints_post": 12,
            "autocorrelation": 0.40,
            "effect_size": 0.20,
            "outcome_sd_input": 1.0,
        },
        "binary": {
            "n_timepoints_pre": 12,
            "n_timepoints_post": 12,
            "autocorrelation": 0.40,
            "baseline_prob": 0.50,
            "effect_size": 0.20,
        },
        "shared": {
            "alpha": 0.05,
            "power": 0.80,
        },
    },
}
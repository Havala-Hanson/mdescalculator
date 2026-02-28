FAMILY_HEADERS = {
    "IRA": {
        "icon": "🧍",
        "title": "Individual Random Assignment",
        "subtitle": "Individuals randomized to treatment or control",
        "description": (
            "Use this design when individuals—not clusters—are randomized. "
            "The model assumes independence across individuals and allows optional covariate adjustment."
        ),
        "background_markdown": r"""
**Model:** \(Y_i = \beta_0 + \delta T_i + e_i\)

**MDES formula** (Bloom et al., 2007):

\[
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{\frac{1 - R^2}{P(1-P)N}}
\]

where \(N\) is total sample size and \(P\) is the treatment proportion.
"""
    },

    "BIRA": {
        "icon": "🧍",
        "title": "Blocked Individual Random Assignment",
        "subtitle": "Individuals randomized within blocks",
        "description": (
            "Use this design when individuals are randomized within blocks such as classrooms or sites. "
            "Block effects may be constant, fixed, or random."
        ),
        "background_markdown": r"""
**Model:** \(Y_{ib} = \beta_0 + \delta T_{ib} + \gamma_b + e_{ib}\)

Blocked individual random assignment adjusts for block-level differences.

**MDES formula**:

\[
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{1 - R^2}{P(1-P)N}
    - \frac{\text{BlockVar}}{P(1-P)B}
}
\]

where \(B\) is number of blocks.
"""
    },

    "CRA": {
        "icon": "🏫",
        "title": "Cluster Random Assignment",
        "subtitle": "Clusters randomized; individuals nested within clusters",
        "description": (
            "Use this design when whole clusters (e.g., schools, clinics) are randomized. "
            "The model accounts for ICC and covariates at each level."
        ),
        "background_markdown": r"""
**Model:** \(Y_{ij} = \beta_0 + \delta T_j + u_j + e_{ij}\)

**MDES formula** (Bloom et al., 2007; Dong & Maynard, 2013):

\[
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho(1 - R^2_2)}{P(1-P)J}
    + \frac{(1-\rho)(1 - R^2_1)}{P(1-P)Jn}
}
\]

where \(\rho\) is ICC, \(J\) clusters, \(n\) cluster size.
"""
    },

    "BCRA": {
        "icon": "🏢",
        "title": "Blocked Cluster Random Assignment",
        "subtitle": "Clusters randomized within blocks",
        "description": (
            "Use this design when clusters are randomized within blocks. "
            "Block effects may be constant, fixed, or random."
        ),
        "background_markdown": r"""
**Model:** \(Y_{ijb} = \beta_0 + \delta T_{jb} + \gamma_b + u_{jb} + e_{ijb}\)

Blocked CRTs adjust for block-level differences.

**MDES formula** (Dong & Maynard, 2013):

\[
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho(1 - R^2_2)}{P(1-P)J}
    + \frac{(1-\rho)(1 - R^2_1)}{P(1-P)Jn}
    - \frac{\text{BlockVar}}{P(1-P)J}
}
\]
"""
    },

    "RD": {
        "icon": "📈",
        "title": "Regression Discontinuity",
        "subtitle": "Treatment assigned by a cutoff",
        "description": (
            "Use this design when treatment is assigned based on a running variable crossing a cutoff. "
            "Power depends on bandwidth, running variable variance, and functional form."
        ),
        "background_markdown": r"""
**Model:** \(Y_i = \beta_0 + \tau D_i + f(X_i - c) + e_i\)

Regression discontinuity identifies a local treatment effect at the cutoff \(c\).

MDES depends on:
- running variable variance
- bandwidth
- functional form
- cluster structure (if applicable)
"""
    },

    "ITS": {
        "icon": "⏱️",
        "title": "Interrupted Time Series",
        "subtitle": "Longitudinal data before and after an intervention",
        "description": (
            "Use this design when repeated measures over time are available before and after an intervention. "
            "Power depends on autocorrelation, trend variance, and number of timepoints."
        ),
        "background_markdown": r"""
**Model:** \(Y_t = \beta_0 + \beta_1 t + \delta D_t + \beta_2 (t \cdot D_t) + e_t\)

Interrupted time series estimates level and slope changes after an intervention.

MDES depends on:
- pre/post timepoints
- autocorrelation
- trend variance
"""
    },
}

FAMILY_CONFIGS = {
    "IRA": {
        "sample_inputs": {
            "fields": ["n_individuals", "p_treat"],
            "recommended": {
                "n_individuals": (200, 2000),
                "p_treat": (0.4, 0.6),
            },
        },
        "icc_inputs": {
            "fields": ["r2_level1"],
            "recommended": {"r2_level1": (0.10, 0.40)},
        },
        "outcome_inputs": {"supports_binary": True, "supports_continuous": True},
        "test_settings": {"fields": ["alpha", "power"]},
        "engine": "compute_mdes_ira",
    },

    "CRA": {
        "sample_inputs": {
            "fields": ["n_clusters", "cluster_size", "p_treat"],
            "recommended": {
                "n_clusters": (20, 60),
                "cluster_size": (15, 35),
                "p_treat": (0.4, 0.6),
            },
        },
        "icc_inputs": {
            "fields": ["icc", "r2_level1", "r2_level2"],
            "recommended": {
                "icc": (0.05, 0.20),
                "r2_level1": (0.10, 0.40),
                "r2_level2": (0.20, 0.60),
            },
        },
        "outcome_inputs": {"supports_binary": True, "supports_continuous": True},
        "test_settings": {"fields": ["alpha", "power"]},
        "engine": "compute_mdes_cra",
    },
    "BIRA": {
        "engine": "compute_mdes_bira",
        "sample_inputs": {
            "fields": ["n_individuals", "n_blocks", "p_treat"],
            "recommended": {
                "n_individuals": [50, 5000],
                "n_blocks": [2, 200],
                "p_treat": [0.3, 0.7],
            },
        },
        "icc_inputs": {
            "fields": ["r2_level1"],
            "recommended": {"r2_level1": [0.0, 0.5]},
        },
        "test_settings": {
            "fields": ["alpha", "power"],
        },
        "outcome_inputs": {
            "fields": ["outcome_type", "baseline_prob", "outcome_sd"],
        },
    },
    "BCRA": {
        "sample_inputs": {
            "fields": ["n_clusters", "cluster_size", "n_blocks", "p_treat"],
            "recommended": {
                "n_clusters": (20, 60),
                "cluster_size": (15, 35),
                "n_blocks": (5, 20),
                "p_treat": (0.4, 0.6),
            },
        },
        "icc_inputs": {
            "fields": ["icc", "r2_level1", "r2_level2"],
            "recommended": {
                "icc": (0.05, 0.20),
                "r2_level1": (0.10, 0.40),
                "r2_level2": (0.20, 0.60),
            },
        },
        "outcome_inputs": {"supports_binary": True, "supports_continuous": True},
        "test_settings": {"fields": ["alpha", "power"]},
        "engine": "compute_mdes_bcra",
    },

    "RD": {
        "sample_inputs": {
            "fields": ["n_units", "bandwidth", "running_var_sd"],
            "recommended": {
                "n_units": (1000, 5000),
                "bandwidth": (0.2, 1.0),
                "running_var_sd": (0.5, 2.0),
            },
        },
        "icc_inputs": {"fields": []},
        "outcome_inputs": {"supports_binary": True, "supports_continuous": True},
        "test_settings": {"fields": ["alpha", "power"]},
        "engine": "compute_mdes_rd",
    },

    "ITS": {
        "sample_inputs": {
            "fields": ["n_timepoints_pre", "n_timepoints_post", "autocorrelation"],
            "recommended": {
                "n_timepoints_pre": (6, 24),
                "n_timepoints_post": (6, 24),
                "autocorrelation": (0.2, 0.6),
            },
        },
        "icc_inputs": {"fields": []},
        "outcome_inputs": {"supports_binary": True, "supports_continuous": True},
        "test_settings": {"fields": ["alpha", "power"]},
        "engine": "compute_mdes_its",
    },
}
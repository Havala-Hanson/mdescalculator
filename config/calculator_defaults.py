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

DESIGN_CONFIGS = {

    # ─────────────────────────────────────────────────────────────
    # IRA — Individual Random Assignment
    # ─────────────────────────────────────────────────────────────
    "IRA": {
        "sample_fields": ["n_individuals"],
        "icc_fields": [],
        "covariate_fields": ["r2_level1"],
        "block_fields": [],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_ira",
    },

    # ─────────────────────────────────────────────────────────────
    # BIRA — Blocked Individual Random Assignment
    # ─────────────────────────────────────────────────────────────
    "BIRA2_1c": {
        "sample_fields": ["n_individuals", "n_blocks"],
        "icc_fields": [],
        "covariate_fields": ["r2_level1", "r2_level2"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bira",
    },

    "BIRA2_1f": {
        "sample_fields": ["n_individuals", "n_blocks"],
        "icc_fields": [],
        "covariate_fields": ["r2_level1", "r2_level2"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bira",
    },

    "BIRA2_1r": {
        "sample_fields": ["n_individuals", "n_blocks"],
        "icc_fields": [],
        "covariate_fields": ["r2_level1", "r2_level2"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bira",
    },

    "BIRA3_1r": {
        "sample_fields": ["n_individuals", "n_blocks"],
        "icc_fields": [],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bira",
    },

    "BIRA4_1r": {
        "sample_fields": ["n_individuals", "n_blocks"],
        "icc_fields": [],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3", "r2_level4"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bira",
    },

    # ─────────────────────────────────────────────────────────────
    # CRA — Cluster Random Assignment
    # ─────────────────────────────────────────────────────────────
    "CRA2_2r": {
        "sample_fields": ["n_clusters", "cluster_size"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2"],
        "block_fields": [],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_cra",
    },

    "CRA3_3r": {
        "sample_fields": ["n_clusters", "cluster_size"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3"],
        "block_fields": [],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_cra",
    },

    "CRA4_4r": {
        "sample_fields": ["n_clusters", "cluster_size"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3", "r2_level4"],
        "block_fields": [],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_cra",
    },

    # ─────────────────────────────────────────────────────────────
    # BCRA — Blocked Cluster Random Assignment
    # ─────────────────────────────────────────────────────────────
    "BCRA3_2f": {
        "sample_fields": ["n_clusters", "cluster_size", "n_blocks"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bcra",
    },

    "BCRA3_2r": {
        "sample_fields": ["n_clusters", "cluster_size", "n_blocks"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bcra",
    },

    "BCRA4_2r": {
        "sample_fields": ["n_clusters", "cluster_size", "n_blocks"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3", "r2_level4"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bcra",
    },

    "BCRA4_3f": {
        "sample_fields": ["n_clusters", "cluster_size", "n_blocks"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3", "r2_level4"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bcra",
    },

    "BCRA4_3r": {
        "sample_fields": ["n_clusters", "cluster_size", "n_blocks"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3", "r2_level4"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": [],
        "engine": "compute_mdes_bcra",
    },

    # ─────────────────────────────────────────────────────────────
    # RD — Regression Discontinuity
    # ─────────────────────────────────────────────────────────────
    "RD2_1f": {
        "sample_fields": ["n_units"],
        "icc_fields": [],
        "covariate_fields": ["r2_level1", "r2_level2"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": ["bandwidth", "running_var_sd"],
        "its_fields": [],
        "engine": "compute_mdes_rd",
    },

    "RD2_1r": {
        "sample_fields": ["n_units"],
        "icc_fields": [],
        "covariate_fields": ["r2_level1", "r2_level2"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": ["bandwidth", "running_var_sd"],
        "its_fields": [],
        "engine": "compute_mdes_rd",
    },

    "RDC_2r": {
        "sample_fields": ["n_units"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2"],
        "block_fields": [],
        "cluster_fields": [],
        "rd_fields": ["bandwidth", "running_var_sd"],
        "its_fields": [],
        "engine": "compute_mdes_rd",
    },

    "RDC_3r": {
        "sample_fields": ["n_units"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3"],
        "block_fields": [],
        "cluster_fields": [],
        "rd_fields": ["bandwidth", "running_var_sd"],
        "its_fields": [],
        "engine": "compute_mdes_rd",
    },

    "RD3_2f": {
        "sample_fields": ["n_units"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": ["bandwidth", "running_var_sd"],
        "its_fields": [],
        "engine": "compute_mdes_rd",
    },

    "RD3_2r": {
        "sample_fields": ["n_units"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": ["bandwidth", "running_var_sd"],
        "its_fields": [],
        "engine": "compute_mdes_rd",
    },

    # ─────────────────────────────────────────────────────────────
    # ITS — Interrupted Time Series
    # ─────────────────────────────────────────────────────────────
    "ITS": {
        "sample_fields": ["n_timepoints_pre", "n_timepoints_post", "n_clusters", "cluster_size"],
        "icc_fields": ["icc"],
        "covariate_fields": ["r2_level1", "r2_level2", "r2_level3"],
        "block_fields": ["n_blocks"],
        "cluster_fields": [],
        "rd_fields": [],
        "its_fields": ["autocorrelation"],
        "engine": "compute_mdes_its",
    },
}
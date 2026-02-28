INPUT_DESCRIPTIONS = {

    # Sample size fields
    "n_individuals": {
        "caption": "Number of individuals included in the study.",
        "tooltip": "For example, the total number of students participating in an individual-level RCT."
    },
    "n_clusters": {
        "caption": "Number of clusters included in the study.",
        "tooltip": "For example, the number of schools participating in a cluster randomized trial."
    },
    "cluster_size": {
        "caption": "Average number of individuals per cluster.",
        "tooltip": "For example, the average number of students per school."
    },
    "n_blocks": {
        "caption": "Number of blocks used for randomization.",
        "tooltip": "For example, grouping schools by size or region before random assignment."
    },
    "n_units": {
        "caption": "Number of units included in the analysis.",
        "tooltip": "For example, the number of students or households in an RD design."
    },
    "n_timepoints_pre": {
        "caption": "Number of time points before the intervention.",
        "tooltip": "For example, 12 months of pre-intervention data in an ITS design."
    },
    "n_timepoints_post": {
        "caption": "Number of time points after the intervention.",
        "tooltip": "For example, 12 months of post-intervention data in an ITS design."
    },

    # Treatment assignment fields
    "p_treat": {
        "caption": "Proportion of units assigned to treatment.",
        "tooltip": "For example, 0.50 means half of individuals or clusters receive treatment."
    },
    "p_block_treat": {
        "caption": "Proportion treated within each block.",
        "tooltip": "For example, if blocks are regions, this is the treatment share within each region."
    },
    "block_prop": {
        "caption": "Proportion of clusters in each block.",
        "tooltip": "For example, if blocks differ in size, this reflects their relative proportions."
    },

    # ICC fields
    "icc": {
        "caption": "Intraclass correlation: proportion of variance between clusters.",
        "tooltip": "For example, the share of student outcome variance attributable to differences between schools."
    },

    # Covariate R² fields (match design levels)
    "r2_level1": {
        "caption": "Proportion of individual-level variance explained by covariates.",
        "tooltip": "For example, student-level covariates like prior achievement or demographics."
    },
    "r2_level2": {
        "caption": "Proportion of second-level variance explained by covariates.",
        "tooltip": "For example, school-level covariates like school size or average prior achievement."
    },
    "r2_level3": {
        "caption": "Proportion of third-level variance explained by covariates.",
        "tooltip": "For example, district-level covariates if your design includes districts above schools."
    },
    "r2_level4": {
        "caption": "Proportion of fourth-level variance explained by covariates.",
        "tooltip": "For example, network- or region-level covariates in a four-level design."
    },

    # RD-specific fields
    "cutoff": {
        "caption": "Value of the running variable at which treatment begins.",
        "tooltip": "For example, a test score threshold that determines eligibility."
    },
    "kernel": {
        "caption": "Weighting function used in RD estimation.",
        "tooltip": "For example, a triangular kernel gives more weight to observations near the cutoff."
    },
    "treatment_side": {
        "caption": "Side of the cutoff where treatment is assigned.",
        "tooltip": "For example, 'right' means units with running variable values above the cutoff receive treatment."
    },
    "bandwidth": {
        "caption": "Range of running variable values used in estimation.",
        "tooltip": "For example, using only students within 0.5 SD of the cutoff."
    },
    "running_var_sd": {
        "caption": "Standard deviation of the running variable.",
        "tooltip": "For example, the SD of the test score used as the running variable."
    },

    # ITS-specific fields
    "autocorrelation": {
        "caption": "Correlation between adjacent time points in the series.",
        "tooltip": "For example, monthly outcomes often show autocorrelation around 0.3–0.5."
    },

    # Outcome fields
    "effect_size": {
        "caption": "Minimum detectable effect size (MDES) or target effect size.",
        "tooltip": "For example, a standardized effect size of 0.20."
    },
    "baseline_prob": {
        "caption": "Baseline probability for binary outcomes.",
        "tooltip": "For example, the proportion of students meeting proficiency before treatment."
    },
    "outcome_sd_input": {
        "caption": "Standard deviation of the outcome measure.",
        "tooltip": "For example, the SD of test scores or other continuous outcomes."
    },

    # Significance and power
    "alpha": {
        "caption": "Significance level for hypothesis testing.",
        "tooltip": "For example, 0.05 corresponds to a 5% Type I error rate."
    },
    "power": {
        "caption": "Desired statistical power.",
        "tooltip": "For example, 0.80 means an 80% chance of detecting the true effect."
    },
}
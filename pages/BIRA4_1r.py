import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bira import compute_mdes_bira4_1r
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BIRA4_1r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    
    # -----------------------------
    # Test settings
    # -----------------------------
    alpha = st.number_input(
        "Significance level (α)",
        min_value=0.001,
        max_value=0.20,
        value=0.05,
        step=0.01,
        help="The significance level (α) is the probability of a Type I error (false positive) (i.e., the threshold for rejecting the null hypothesis). Common values are 0.05 (5% significance level) or 0.01 (1% significance level). Lower α requires stronger evidence to reject the null hypothesis, which typically increases required sample sizes.",
    )

    power = st.number_input(
        "Power (1 - β)",
        min_value=0.50,
        max_value=0.99,
        value=0.80,
        step=0.05,
        help="Power is the probability of correctly rejecting the null hypothesis when there is a true effect. Common values are 0.80 (80% power) or 0.90 (90% power). Higher power requires larger sample sizes.",
    )

    two_tailed = st.radio(
        "Two-tailed or one-tailed test?",
        options=[True, False],
        format_func=lambda x: "Two‑tailed" if x else "One‑tailed",
        index=0,
        help = "Two-tailed tests are more conservative and test for effects in both directions. One-tailed tests have more power to detect an effect in a specified direction but cannot detect effects in the opposite direction. Default: Two-tailed.",
    )
    
    # -----------------------------
    # Four-level blocked IRA structure
    # L = blocks, K = sites per block, J = clusters per site, n = cluster size
    # -----------------------------
    n_blocks = st.number_input(
        "Number of level-4 blocks (L)",
        min_value=2,
        value=5,
        step=1,
        help="Number of level-4 blocks (e.g., districts, regions). Default: 5.",
    )

    n_sites_per_block = st.number_input(
        "Number of level-3 sites per block (K)",
        min_value=1,
        value=4,
        step=1,
        help="Number of level-3 sites (e.g., schools, clinics) per block. Default: 4.",
    )

    n_clusters_per_site = st.number_input(
        "Number of level-2 clusters per site (J)",
        min_value=1,
        value=5,
        step=1,
        help="Number of level-2 clusters (e.g., classrooms, patient groups) per site. Default: 5.",
    )

    cluster_size = st.number_input(
        "Average cluster size (n, individuals per cluster)",
        min_value=2,
        value=20,
        step=1,
        help="Average number of individuals per cluster. Default: 20.",
    )

    prop_treated = st.number_input(
        "Proportion treated (p)",
        min_value=0.05,
        max_value=0.95,
        value=0.50,
        step=0.05,
        help="Proportion of clusters assigned to treatment. Default: 0.50.",
    )

    # -----------------------------
    # ICCs and variance components
    # -----------------------------
    icc2 = st.number_input(
        "ICC at level 2 (clusters, ρ₂)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
        help="Intraclass correlation coefficient at level 2 (clusters): Proportion of variance in outcome explained by clusters (V2/(V1+V2+V3+V4)). Default: 0.05.",
    )

    icc3 = st.number_input(
        "ICC at level 3 (sites, ρ₃)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
        help="Intraclass correlation coefficient at level 3 (sites): Proportion of variance in outcome explained by sites (V3/(V1+V2+V3+V4)). Default: 0.05.",
    )

    icc4 = st.number_input(
        "ICC at level 4 (blocks, ρ₄)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
        help="Intraclass correlation coefficient at level 4 (blocks): Proportion of variance in outcome explained by blocks (V4/(V1+V2+V3+V4)). Default: 0.05.",
    )

    omega2 = st.number_input(
        "Proportion of level-2 variance that is treatment-relevant (ω₂)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
        help="Proportion of level-2 variance that is explained by treatment assignment. Default: 1.0 (treatment explains all cluster-level variance).",
    )

    omega3 = st.number_input(
        "Proportion of level-3 variance that is treatment-relevant (ω₃)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
        help="Proportion of level-3 variance that is explained by treatment assignment. Default: 1.0 (treatment explains all site-level variance).",
    )

    omega4 = st.number_input(
        "Proportion of level-4 variance that is treatment-relevant (ω₄)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
        help="Proportion of level-4 variance that is explained by treatment assignment. Default: 1.0 (treatment explains all block-level variance).",
    )

    # -----------------------------
    # Covariates (R² at each level)
    # -----------------------------
    r2_level1 = st.number_input(
        "R² (individual-level covariates, R²₁)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="R² for individual-level covariates (proportion of variance in outcome explained by individual-level covariates). Default: 0.0."
    )

    r2_level2 = st.number_input(
        "R² (cluster-level covariates, R²₂)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="R² for cluster-level covariates (proportion of variance in outcome explained by cluster-level covariates). Default: 0.0."
    )

    r2_level3 = st.number_input(
        "R² (site-level covariates, R²₃)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="R² for site-level covariates (proportion of variance in outcome explained by site-level covariates). Default: 0.0."
    )

    r2_level4 = st.number_input(
        "R² (block-level covariates, R²₄)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="R² for block-level covariates (proportion of variance in outcome explained by block-level covariates). Default: 0.0."
    )

    # -----------------------------
    # Outcome type
    # -----------------------------
    outcome_type = st.selectbox(
        "Outcome type",
        ["continuous", "binary"],
        index=0,
    )

    baseline_prob = None
    outcome_sd = None

    if outcome_type == "binary":
        baseline_prob = st.number_input(
            "Baseline probability",
            min_value=0.01,
            max_value=0.99,
            value=0.50,
            step=0.01,
            help="Baseline probability of the outcome in the control group. Default: 0.50.",
        )
    else:
        outcome_sd = st.number_input(
            "Outcome SD (standardized units)",
            min_value=0.01,
            value=1.0,
            step=0.1,
            help="Standard deviation of the outcome variable in standardized units. Default: 1.0.",
        )

    # -----------------------------
    # Return engine inputs
    # -----------------------------
    return {
        "n_blocks": n_blocks,
        "n_sites_per_block": n_sites_per_block,
        "n_clusters_per_site": n_clusters_per_site,
        "cluster_size": cluster_size,
        "prop_treated": prop_treated,
        "icc2": icc2,
        "icc3": icc3,
        "icc4": icc4,
        "omega2": omega2,
        "omega3": omega3,
        "omega4": omega4,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "r2_level3": r2_level3,
        "r2_level4": r2_level4,
        "alpha": alpha,
        "power": power,
        "two_tailed": two_tailed,
        "outcome_type": outcome_type,
        "baseline_prob": baseline_prob,
        "outcome_sd": outcome_sd,
    }


def render():
    render_calculator_page(
        design=design,
        input_render_fn=render_inputs,
        engine_fn=compute_mdes_bira4_1r,
    )

render()
import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bira import compute_mdes_bira3_1r
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BIRA3_1r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    
    # ------------------------------------------------------------
    # Test settings
    # ------------------------------------------------------------
    prop_treated = st.number_input("Proportion treated (p)", 0.05, 0.95, 0.50, 0.05,
                                   help="Proportion of individuals who are treated in the study.")
    alpha = st.number_input("Significance level (α)", 0.001, 0.20, 0.05, 0.01,
        help="The significance level (α) is the probability of a Type I error (false positive) (i.e., the threshold for rejecting the null hypothesis). Common values are 0.05 (5% significance level) or 0.01 (1% significance level). Lower α requires stronger evidence to reject the null hypothesis, which typically increases required sample sizes.",
    )
    power = st.number_input("Power (1 − β)", 0.50, 0.99, 0.80, 0.05, 
        help="Power is the probability of correctly rejecting the null hypothesis when there is a true effect. Common values are 0.80 (80% power) or 0.90 (90% power). Higher power requires larger sample sizes.",
    )
    two_tailed = st.radio(
        "Two-tailed or one-tailed test?",
        options=[True, False],
        format_func=lambda x: "Two‑tailed" if x else "One‑tailed",
        index=0,
        help = "Two-tailed tests are more conservative and test for effects in both directions. One-tailed tests have more power to detect an effect in a specified direction but cannot detect effects in the opposite direction. Default: Two-tailed.",
    )

    # ------------------------------------------------------------
    # Three-level sample structure
    # ------------------------------------------------------------
    n_blocks = st.number_input(
        "Number of level‑3 blocks (K)",
        min_value=2,
        value=20,
        step=1,
        help="Number of level-3 blocks (e.g., districts, schools). More blocks generally increase power, but with diminishing returns. Default: 20.",
    )

    n_clusters_per_block = st.number_input(
        "Clusters per block (J)",
        min_value=1,
        value=5,
        step=1,
        help="Number of clusters (e.g., schools, clinics) per block. More clusters generally increase power, but with diminishing returns. Default: 5.",
    )

    cluster_size = st.number_input(
        "Individuals per cluster (n)",
        min_value=2,
        value=20,
        step=1,
        help="Average number of individuals per cluster. More individuals per cluster generally increase power, but with diminishing returns. Default: 20.",
    )

    # ------------------------------------------------------------
    # ICCs
    # ------------------------------------------------------------
    icc3 = st.number_input(
        "ICC at block level (ρ₃)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
        help="Intraclass correlation coefficient at block level: Proportion of variance in outcome explained by blocks (V3/(V1+V2+V3)). Higher values indicate more similarity within blocks, which can decrease power. Default: 0.05.",
    )

    icc2 = st.number_input(
        "ICC at cluster level (ρ₂)",
        min_value=0.0,
        max_value=0.99,
        value=0.10,
        step=0.01,
        help="Intraclass correlation coefficient at cluster level: Proportion of variance in outcome explained by clusters (V2/(V1+V2+V3)). Higher values indicate more similarity within clusters, which can decrease power. Default: 0.10.",
    )

    # ------------------------------------------------------------
    # Treatment‑explained variance (omegas)
    # ------------------------------------------------------------
    omega3 = st.number_input(
        "ω₃ (treatment share of level‑3 variance)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
        help="Proportion of block-level variance that is explained by treatment assignment. Higher values indicate a larger treatment effect at the block level, which can increase power. Default: 1.0 (treatment explains all block-level variance).",
    )

    omega2 = st.number_input(
        "ω₂ (treatment share of level‑2 variance)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
        help="Proportion of cluster-level variance that is explained by treatment assignment. Higher values indicate a larger treatment effect at the cluster level, which can increase power. Default: 1.0 (treatment explains all cluster-level variance).",
    )

    # ------------------------------------------------------------
    # Covariate R²
    # ------------------------------------------------------------
    r2_level1 = st.number_input("R² level 1 (r₂₁)", 0.0, 0.99, 0.0, 0.05,
                                help="R² for level-1 covariates (proportion of variance in outcome explained by level-1 covariates). More explained variance can increase power. Default: 0.0.")
    r2_level2 = st.number_input("R² level 2 (r₂t₂)", 0.0, 0.99, 0.0, 0.05,
                                help="R² for level-2 covariates (proportion of variance in outcome explained by level-2 covariates). More explained variance can increase power. Default: 0.0.")
    r2_level3 = st.number_input("R² level 3 (r₂t₃)", 0.0, 0.99, 0.0, 0.05,
                                help="R² for level-3 covariates (proportion of variance in outcome explained by level-3 covariates). More explained variance can increase power. Default: 0.0.")
    g3 = st.number_input(
        "Number of level-3 covariates (g3)",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        help="Number of level-3 covariates included in the model for degrees‑of‑freedom adjustment. More covariates reduce the available degrees of freedom, which can slightly increase the MDES. Default: 0.",
    )
    # ------------------------------------------------------------
    # Outcome type
    # ------------------------------------------------------------
    outcome_type = st.selectbox("Outcome type", ["continuous", "binary"], index=0)

    baseline_prob = None
    outcome_sd = None
    if outcome_type == "binary":
        baseline_prob = st.number_input("Baseline probability", 0.01, 0.99, 0.50, 0.01,
                                        help="Baseline probability of the outcome in the control group (for binary outcomes). More extreme probabilities can increase the required sample size. Default: 0.50.")
    else:
        outcome_sd = st.number_input("Outcome SD (standardized)", 0.01, value=1.0, step=0.1,
                                     help="Standard deviation of the outcome variable in standardized units. Higher values indicate more variability in the outcome, which can increase the required sample size. Default: 1.0 (standardized outcome).")

    return {
        "n_blocks": n_blocks,
        "n_clusters_per_block": n_clusters_per_block,
        "cluster_size": cluster_size,
        "icc2": icc2,
        "icc3": icc3,
        "omega2": omega2,
        "omega3": omega3,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "r2_level3": r2_level3,
        "alpha": alpha,
        "power": power,
        "two_tailed": two_tailed,
        "outcome_type": outcome_type,
        "baseline_prob": baseline_prob,
        "outcome_sd": outcome_sd,
        "prop_treated": prop_treated,
    }


def render():
    render_calculator_page(
        design=design,
        input_render_fn=render_inputs,
        engine_fn=compute_mdes_bira3_1r,
        sensitivity_fields=["n_blocks", "n_clusters_per_block", "cluster_size", "icc2", "icc3", "omega2", "omega3", "r2_level1", "r2_level2", "r2_level3"],
    )

render()
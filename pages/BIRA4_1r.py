import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bira import compute_mdes_bira4_1r
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BIRA4_1r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    # -----------------------------
    # Four-level blocked IRA structure
    # L = blocks, K = sites per block, J = clusters per site, n = cluster size
    # -----------------------------
    n_blocks = st.number_input(
        "Number of level-4 blocks (L)",
        min_value=2,
        value=design.defaults.get("n_blocks", 5),
        step=1,
    )

    n_sites_per_block = st.number_input(
        "Number of level-3 sites per block (K)",
        min_value=1,
        value=design.defaults.get("n_sites_per_block", 4),
        step=1,
    )

    n_clusters_per_site = st.number_input(
        "Number of level-2 clusters per site (J)",
        min_value=1,
        value=design.defaults.get("n_clusters_per_site", 5),
        step=1,
    )

    cluster_size = st.number_input(
        "Average cluster size (n, individuals per cluster)",
        min_value=2,
        value=design.defaults.get("cluster_size", 20),
        step=1,
    )

    prop_treated = st.number_input(
        "Proportion treated (p)",
        min_value=0.05,
        max_value=0.95,
        value=0.50,
        step=0.05,
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
    )

    icc3 = st.number_input(
        "ICC at level 3 (sites, ρ₃)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
    )

    icc4 = st.number_input(
        "ICC at level 4 (blocks, ρ₄)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
    )

    omega2 = st.number_input(
        "Proportion of level-2 variance that is treatment-relevant (ω₂)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
    )

    omega3 = st.number_input(
        "Proportion of level-3 variance that is treatment-relevant (ω₃)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
    )

    omega4 = st.number_input(
        "Proportion of level-4 variance that is treatment-relevant (ω₄)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
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
    )

    r2_level2 = st.number_input(
        "R² (cluster-level covariates, R²₂)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
    )

    r2_level3 = st.number_input(
        "R² (site-level covariates, R²₃)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
    )

    r2_level4 = st.number_input(
        "R² (block-level covariates, R²₄)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
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
        )
    else:
        outcome_sd = st.number_input(
            "Outcome SD (raw units)",
            min_value=0.01,
            value=1.0,
            step=0.1,
        )

    # -----------------------------
    # Test settings
    # -----------------------------
    alpha = st.number_input(
        "Significance level (α)",
        min_value=0.001,
        max_value=0.20,
        value=0.05,
        step=0.01,
    )

    power = st.number_input(
        "Power (1 - β)",
        min_value=0.50,
        max_value=0.99,
        value=0.80,
        step=0.05,
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
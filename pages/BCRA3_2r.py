# pages/BCRA3_2r.py

import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bcra import compute_mdes_bcra3_2r
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BCRA3_2r"
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
        help="Power is the probability of correctly rejecting the null hypothesis when there is a true effect. Common values are 0.80 (80% power) or 0.90 (90% power). Higher power requires larger sample sizes.",
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
    # Three-level structure
    # -----------------------------
    n_level3 = st.number_input(
        "Number of level-3 blocks (K)",
        min_value=1,
        value=50,
        step=1,
        help="Number of level-3 blocks (e.g., schools). Increasing K increases the number of randomized units (K × J), which improves power. In this design, blocks also contribute treatment-effect heterogeneity (ω₃), so more blocks help stabilize those estimates. Default: 50."
    )

    n_level2 = st.number_input(
        "Number of level-2 units per block (J)",
        min_value=3,
        value=5,
        step=1,
        help="Number of level-2 units (e.g., classrooms) within each block. Increasing J increases the number of randomized units (K × J), which improves power, with diminishing returns when ICC2 is high. Default: 5."
        )

    cluster_size = st.number_input(
        "Average number of level-1 units per level-2 unit (n)",
        min_value=1,
        value=30,
        step=1,
       help="Average number of level-1 units (e.g., individuals) per level-2 unit. Larger cluster sizes reduce the within-cluster variance component, improving power, though gains diminish when ICC2 is high. Default: 30."
       )

    # -----------------------------
    # ICCs
    # -----------------------------
    icc3 = st.number_input(
        "ICC (level 3)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
        help="Intraclass correlation at level 3 (e.g., schools). Represents the proportion of outcome variance between blocks. This variance is separate from treatment-effect heterogeneity (ω₃). Higher ICC3 increases the between-block outcome variance component. Default: 0.05."
        )

    icc2 = st.number_input(
        "ICC (level 2)",
        min_value=0.0,
        max_value=0.99,
        value=0.10,
        step=0.01,
        help="Intraclass correlation at level 2 (e.g., classrooms). Represents the proportion of outcome variance between level-2 units. Higher ICC2 increases the between-cluster variance component and typically increases the MDES. Default: 0.10."
        )

    omega3 = st.number_input(
        "Treatment-effect heterogeneity across blocks (ω₃)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        help="Treatment-effect heterogeneity across blocks. ω₃ represents the ratio of treatment-effect variance to outcome variance at the block level. ω₃ = 0 means treatment effects are constant across blocks; higher values indicate more variation in treatment effects. This term increases the MDES but is not reduced by covariates. Default: 1.0."
        )

    # -----------------------------
    # Covariates
    # -----------------------------
    r2_level1 = st.number_input(
        "R² (level-1 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of level-1 (individual-level) variance explained by covariates. Higher values reduce residual variance and lower the MDES. Default: 0.0."
        )

    r2_level2 = st.number_input(
        "R² (level-2 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of level-2 (cluster-level) variance explained by covariates. Higher values reduce between-cluster variance and lower the MDES. Default: 0.0."
        )

    r2_level3 = st.number_input(
        "R² (level-3 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of level-3 (block-level) outcome variance explained by covariates. This reduces the outcome ICC3 component but does not reduce treatment-effect heterogeneity (ω₃). Default: 0.0."
        )

    g3 = st.number_input(
        "Number of level-3 covariates (g₃)",
        min_value=0,
        value=0,
        step=1,
        help="Number of block-level covariates included in the model. These reduce degrees of freedom: df = K − g₃ − 1. More covariates can reduce variance but also reduce df, which can increase the MDES. Default: 0."
        )

    # -----------------------------
    # Outcome type
    # -----------------------------
    outcome_type = st.selectbox(
        "Outcome type",
        ["continuous", "binary"],
        index=0,
        help="Type of outcome variable. Continuous outcomes are measured on a numeric scale (e.g., test scores), while binary outcomes have two categories (e.g., pass/fail). This choice affects the calculation of the standard deviation and the MDES. Default: Continuous.",
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
            help="Baseline probability of the outcome in the control group. Determines the variance of a binary outcome: p(1−p). Values near 0 or 1 reduce variance and can increase the MDES. Default: 0.50."
            )
    else:
        outcome_sd = st.number_input(
            "Outcome SD (raw units)",
            min_value=0.01,
            value=1.0,
            step=0.1,
            help="Standard deviation of the continuous outcome. Larger SD values indicate more variability and increase the MDES. Default: 1.0."
            )

    # -----------------------------
    # Return engine inputs
    # -----------------------------
    return {
        "n_level3": n_level3,
        "n_level2": n_level2,
        "cluster_size": cluster_size,
        "icc3": icc3,
        "icc2": icc2,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "r2_level3": r2_level3,
        "omega3": omega3,
        "g3": g3,
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
        engine_fn=compute_mdes_bcra3_2r,
        sensitivity_fields=["n_level3", "n_level2", "cluster_size", "icc2", "icc3", "omega3", "r2_level1", "r2_level2", "r2_level3"],
    )

render()
# pages/CRA4_4r.py

import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.mdes_four_level import compute_mdes_cra4_4
from services.calculator_template import render_calculator_page


DESIGN_CODE = "CRA4_4r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
     # -----------------------------
    # Test settings
    # -----------------------------
    p_treat = st.number_input(
        "Treatment proportion (p)",
        min_value=0.01,
        max_value=0.99,
        value=0.50,
        step=0.01,
        help="Proportion of level-4 units assigned to treatment. R default: 0.50.",
    )

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
    # Four-level structure
    # -----------------------------
    n_level4 = st.number_input(
        "Number of level-4 units (L4)",
        min_value=3,
        value=20,
        step=1,
    )

    n_level3 = st.number_input(
        "Number of level-3 units per level-4 unit (L3 per L4)",
        min_value=1,
        value=5,
        step=1,
    )

    n_level2 = st.number_input(
        "Number of level-2 units per level-3 unit (L2 per L3)",
        min_value=1,
        value=5,
        step=1,
    )

    cluster_size = st.number_input(
        "Average number of level-1 units per level-2 unit (n)",
        min_value=1,
        value=30,
        step=1,
    )

    # -----------------------------
    # ICCs
    # -----------------------------
    icc4 = st.number_input(
        "ICC (level 4)",
        min_value=0.0,
        max_value=0.99,
        value=0.02,
        step=0.01,
    )

    icc3 = st.number_input(
        "ICC (level 3)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
    )

    icc2 = st.number_input(
        "ICC (level 2)",
        min_value=0.0,
        max_value=0.99,
        value=0.10,
        step=0.01,
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
    )

    r2_level2 = st.number_input(
        "R² (level-2 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
    )

    r2_level3 = st.number_input(
        "R² (level-3 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
    )

    r2_level4 = st.number_input(
        "R² (level-4 covariates)",
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
    # Return engine inputs
    # -----------------------------
    return {
        "n_level4": n_level4,
        "n_level3": n_level3,
        "n_level2": n_level2,
        "cluster_size": cluster_size,
        "icc4": icc4,
        "icc3": icc3,
        "icc2": icc2,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "r2_level3": r2_level3,
        "r2_level4": r2_level4,
        "p_treat": p_treat,
        "two_tailed": two_tailed,
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
        engine_fn=compute_mdes_cra4_4,
    )

render()
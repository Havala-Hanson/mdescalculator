# pages/CRA3_3r.py

import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.mdes_three_level import compute_mdes_cra3_3
from services.calculator_template import render_calculator_page


DESIGN_CODE = "CRA3_3r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    # -----------------------------
    # Three-level structure
    # -----------------------------
    n_level3 = st.number_input(
        "Number of level-3 units (K)",
        min_value=3,
        value=design.defaults.get("n_level3", 20),
        step=1,
    )

    n_level2 = st.number_input(
        "Number of level-2 units per level-3 unit (J)",
        min_value=1,
        value=design.defaults.get("n_level2", 5),
        step=1,
    )

    cluster_size = st.number_input(
        "Average number of level-1 units per level-2 unit (n)",
        min_value=1,
        value=design.defaults.get("cluster_size", 30),
        step=1,
    )

    # -----------------------------
    # ICCs
    # -----------------------------
    icc3 = st.number_input(
        "ICC (level 3)",
        min_value=0.0,
        max_value=0.99,
        value=design.defaults.get("icc3", 0.05),
        step=0.01,
    )

    icc2 = st.number_input(
        "ICC (level 2)",
        min_value=0.0,
        max_value=0.99,
        value=design.defaults.get("icc2", 0.10),
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
    two_tailed = st.checkbox(
        "Two-tailed test",
        value=True,
    )

    p_treat = st.number_input(
        "Treatment proportion (p)",
        min_value=0.01,
        max_value=0.99,
        value=0.50,
        step=0.01,
        help="Proportion of level-3 units assigned to treatment. R default: 0.50.",
    )

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
        "n_level3": n_level3,
        "n_level2": n_level2,
        "cluster_size": cluster_size,
        "icc3": icc3,
        "icc2": icc2,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "r2_level3": r2_level3,
        "p_treat": p_treat,
        "two_tailed": two_tailed,
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
        engine_fn=compute_mdes_cra3_3,
    )
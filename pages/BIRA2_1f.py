import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bira import compute_mdes_bira2_1f
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BIRA2_1f"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):

    # ------------------------------------------------------------
    # Two-level blocked IRA structure (fixed block effects)
    # ------------------------------------------------------------
    n_blocks = st.number_input(
        "Number of blocks (J)",
        min_value=2,
        value=20,
        step=1,
    )

    n_individuals = st.number_input(
        "Total number of individuals (N = J × n)",
        min_value=4,
        value=200,
        step=10,
    )

    # ------------------------------------------------------------
    # Covariates (only level‑1 used in variance)
    # ------------------------------------------------------------
    r2_level1 = st.number_input(
        "R² (individual-level covariates, r²₁)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
    )

    # ------------------------------------------------------------
    # Outcome type
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # Test settings
    # ------------------------------------------------------------
    alpha = st.number_input(
        "Significance level (α)",
        min_value=0.001,
        max_value=0.20,
        value=0.05,
        step=0.01,
    )

    power = st.number_input(
        "Power (1 − β)",
        min_value=0.50,
        max_value=0.99,
        value=0.80,
        step=0.05,
    )

    # ------------------------------------------------------------
    # Return engine inputs
    # ------------------------------------------------------------
    return {
        "n_individuals": n_individuals,
        "n_blocks": n_blocks,
        "r2_level1": r2_level1,
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
        engine_fn=compute_mdes_bira2_1f,
    )
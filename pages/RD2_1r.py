import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.rd import compute_mdes_rd
from services.calculator_template import render_calculator_page


DESIGN_CODE = "RD2_1r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    # -----------------------------
    # Running variable and cutoff
    # -----------------------------
    cutoff = st.number_input(
        "Cutoff value",
        value=0.0,
        step=0.1,
    )

    bandwidth = st.number_input(
        "Bandwidth (h)",
        min_value=0.01,
        value=1.0,
        step=0.1,
    )

    # -----------------------------
    # Kernel choice
    # -----------------------------
    kernel = st.selectbox(
        "Kernel",
        ["triangular", "uniform", "epanechnikov"],
        index=0,
    )

    # -----------------------------
    # Treatment side
    # -----------------------------
    treatment_side = st.selectbox(
        "Treatment side",
        ["right", "left"],
        index=0,
    )

    # -----------------------------
    # Covariates
    # -----------------------------
    r2_level1 = st.number_input(
        "R² (individual-level covariates)",
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
        "cutoff": cutoff,
        "bandwidth": bandwidth,
        "kernel": kernel,
        "treatment_side": treatment_side,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
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
        engine_fn=compute_mdes_rd,
    )

render()
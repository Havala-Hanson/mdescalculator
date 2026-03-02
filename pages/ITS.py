import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.its import compute_mdes_its
from services.calculator_template import render_calculator_page


DESIGN_CODE = "ITS"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    # -----------------------------
    # Time structure
    # -----------------------------
    n_timepoints_pre = st.number_input(
        "Number of pre-intervention time points",
        min_value=2,
        value=8,
        step=1,
    )

    n_timepoints_post = st.number_input(
        "Number of post-intervention time points",
        min_value=2,
        value=8,
        step=1,
    )

    autocorrelation = st.number_input(
        "Autocorrelation (ρ)",
        min_value=0.0,
        max_value=0.99,
        value=0.30,
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

    return {
        "n_timepoints_pre": n_timepoints_pre,
        "n_timepoints_post": n_timepoints_post,
        "autocorrelation": autocorrelation,
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
        engine_fn=compute_mdes_its,
    )

render()
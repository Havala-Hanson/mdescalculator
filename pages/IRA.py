import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.ira import compute_mdes_ira
from services.calculator_template import render_calculator_page


DESIGN_CODE = "IRA"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    n_individuals = st.number_input(
        "Total number of individuals (N)",
        min_value=4,
        value=200,
        step=10,
    )

    r2_level1 = st.number_input(
        "R² from covariates",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
    )

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

    p = st.number_input(
        "Treatment proportion (p)",
        min_value=0.01,
        max_value=0.99,
        value=0.50,
        step=0.01,
        help="Proportion of individuals assigned to treatment. R default: 0.50.",
    )

    g1 = st.number_input(
        "Number of covariates (g1)",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        help="Number of covariates for degrees of freedom adjustment. R default: 0.",
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

    return {
        "n_individuals": n_individuals,
        "r2_level1": r2_level1,
        "p": p,
        "g1": g1,
        "outcome_type": outcome_type,
        "baseline_prob": baseline_prob,
        "outcome_sd": outcome_sd,
        "alpha": alpha,
        "power": power,
    }


def render():
    render_calculator_page(
        design=design,
        input_render_fn=render_inputs,
        engine_fn=compute_mdes_ira,
    )

render()
import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.ira import compute_mdes_ira
from services.calculator_template import render_calculator_page


DESIGN_CODE = "IRA"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    
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

    n_individuals = st.number_input(
        "Total number of individuals (N)",
        min_value=4,
        value=200,
        step=10,
        help="Total number of individuals in the study. Must be at least 4. More individuals generally increase power. Default: 200.",
    )
    
    r2_level1 = st.number_input(
        "R² from covariates",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of variance in the outcome explained by covariates. Higher values reduce residual variance and therefore reduce the MDES. Default: 0.0 (no covariates).")

    g1 = st.number_input(
        "Number of covariates for df adjustment (g1)",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        help="Number of level-1 covariates included in the model for degrees‑of‑freedom adjustment. More covariates reduce the available degrees of freedom, which can slightly increase the MDES. Default: 0.",
    )
    
    outcome_type = st.selectbox(
        "Outcome type",
        ["continuous", "binary"],
        index=0,
        help="Type of outcome variable. Continuous outcomes are measured on a numeric scale (e.g., test scores). Binary outcomes have two categories (e.g., success/failure). Default: continuous.",
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
            help="“Baseline probability of the outcome in the control group. Determines the variance of a binary outcome, which affects the MDES in percentage‑point units. Variance is highest at 0.50. Default: 0.50.",
        )
    else:
        outcome_sd = st.number_input(
            "Outcome SD (raw units)",
            min_value=0.01,
            value=1.0,
            step=0.1,
            help="Standard deviation of the outcome in raw units. Larger values increase the MDES when expressed in raw units. Only needed for continuous outcomes. Default: 1.0.",
        )

    p = st.number_input(
        "Treatment proportion (p)",
        min_value=0.01,
        max_value=0.99,
        value=0.50,
        step=0.01,
        help="Proportion of individuals assigned to treatment. MDES is minimized when p = 0.50 and increases as the allocation becomes more unbalanced. Default: 0.50.",
    )

    return {
        "n_individuals": n_individuals,
        "two_tailed": two_tailed,
        "r2_level1": r2_level1,
        "g1": g1,
        "p": p,
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
        sensitivity_fields=["n_individuals", "r2_level1", "g1", "p"],
    )

render()
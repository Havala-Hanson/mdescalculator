import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bira import compute_mdes_bira2_1c
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BIRA2_1c"
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
        "Power (1 − β)",
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

    n_blocks = st.number_input(
        "Number of blocks (J)",
        min_value=2,
        value=design.calculator_config.get("defaults", {}).get("n_blocks", 20),
        step=1,
        help="Number of blocks (clusters) in the design. More blocks generally increase power, but with diminishing returns. Default: 20.",
    )

    n_individuals = st.number_input(
        "Total number of individuals (N = J × n)",
        min_value=4,
        value=design.calculator_config.get("defaults", {}).get("n_individuals", 200),
        step=10,
        help="Total number of individuals in the study (N). This is the product of the number of blocks (J) and the number of individuals per block (n). More individuals generally increase power. Default: 200.",
    )

    r2_level1 = st.number_input(
        "R² (individual-level covariates, level 1)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of individual-level variance explained by individual-level covariates. More explained variance can increase power. Default: 0.0.",
    )

    n_covariates_level1 = st.number_input(
        "Number of level-1 covariates in the model (g₁)",
        min_value=0,
        value=0,
        step=1,
        help="Number of individual-level covariates included in the model. Reduces degrees of freedom: df = N - g₁ - 2. Higher values can increase the required sample size. Default: 0.",
    )

    outcome_type = st.selectbox(
        "Outcome type",
        ["continuous", "binary"],
        index=0,
        help="Type of outcome variable. Continuous outcomes are measured on a numeric scale (e.g., test scores), while binary outcomes have two categories (e.g., pass/fail). This affects the calculation of the standard error and may require additional parameters (e.g., baseline probability for binary outcomes). Default: continuous.",
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
            help="Baseline probability of the outcome in the control group. Higher values indicate a higher proportion of the control group having the outcome, which can increase the required sample size. Default: 0.50.",
        )
    else:
        outcome_sd = st.number_input(
            "Outcome SD (raw units)",
            min_value=0.01,
            value=1.0,
            step=0.1,
            help="Standard deviation of the outcome in raw units. Higher values indicate more variability in the outcome, which can increase the required sample size. Only needed for continuous outcomes. Default: 1.0.",

        )

    prop_treated = st.number_input(
        "Proportion treated (p)",
        min_value=0.05,
        max_value=0.95,
        value=0.50,
        step=0.05,
        help="Proportion of individuals assigned to the treatment group. Higher values indicate a larger treatment effect, which can increase the required sample size. Default: 0.50.",
    )

    return {
        "n_individuals": n_individuals,
        "n_blocks": n_blocks,
        "r2_level1": r2_level1,
        "alpha": alpha,
        "power": power,
        "two_tailed": two_tailed,
        "outcome_type": outcome_type,
        "baseline_prob": baseline_prob,
        "outcome_sd": outcome_sd,
        "prop_treated": prop_treated,
        "n_covariates_level1": n_covariates_level1,
    }


def render():
    render_calculator_page(
        design=design,
        input_render_fn=render_inputs,
        engine_fn=compute_mdes_bira2_1c,
        sensitivity_fields=["n_individuals", "n_blocks", "r2_level1"],
    )

render()
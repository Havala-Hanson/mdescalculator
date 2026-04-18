import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bira import compute_mdes_bira2_1f
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BIRA2_1f"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    
    # ------------------------------------------------------------
    # Test settings
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # Two-level blocked IRA structure (fixed block effects)
    # ------------------------------------------------------------
    n_blocks = st.number_input(
        "Number of blocks (J)",
        min_value=2,
        value=20,
        step=1,
        help="Number of blocks (clusters) in the design. More blocks generally increase power, but with diminishing returns. Default: 20.",
    )

    n_individuals = st.number_input(
        "Total number of individuals (N = J × n)",
        min_value=4,
        value=200,
        step=10,
        help="Total number of individuals in the study (N). This is the product of the number of blocks (J) and the number of individuals per block (n). More individuals generally increase power. Default: 200.",
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
        help="Proportion of individual-level variance explained by individual-level covariates. More explained variance can increase power. Default: 0.0.",
    )

    n_covariates_level1 = st.number_input(
        "Number of level-1 covariates (g1)",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        help="Number of level-1 covariates included in the model for degrees‑of‑freedom adjustment. More covariates reduce the available degrees of freedom, which can slightly increase the MDES. Default: 0.",
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

    # ------------------------------------------------------------
    # Return engine inputs
    # ------------------------------------------------------------
    return {
        "n_individuals": n_individuals,
        "n_blocks": n_blocks,
        "r2_level1": r2_level1,
        "n_covariates_level1": n_covariates_level1, 
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
        engine_fn=compute_mdes_bira2_1f,
        sensitivity_fields=["n_individuals", "n_blocks", "r2_level1", "n_covariates_level1"],
    )

render()
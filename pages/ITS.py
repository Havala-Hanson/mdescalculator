import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.its import compute_mdes_its
from services.calculator_template import render_calculator_page


DESIGN_CODE = "ITS"
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
    # Time structure
    # -----------------------------
    n_timepoints_pre = st.number_input(
        "Number of pre-intervention time points",
        min_value=2,
        value=8,
        step=1,
        help="The number of time points observed before the intervention is implemented. It should be at least 2 to allow for estimation of a pre-intervention trend. More pre-intervention time points generally increase power.",
    )

    n_timepoints_post = st.number_input(
        "Number of post-intervention time points",
        min_value=2,
        value=8,
        step=1,
        help="The number of time points observed after the intervention is implemented. It should be at least 2 to allow for estimation of a post-intervention trend. More post-intervention time points generally increase power.",
    )

    autocorrelation = st.number_input(
        "Autocorrelation (ρ)",
        min_value=0.0,
        max_value=0.99,
        value=0.30,
        step=0.05,
        help="The autocorrelation (ρ) represents the correlation of the outcome variable with itself across time points. It should be between 0.0 and 0.99. Higher autocorrelation typically increases required sample sizes.",
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
            help="The baseline probability is the expected proportion of 'successes' (e.g., events, cases) in the outcome variable before the intervention. It should be between 0.01 and 0.99. Default: 0.50.",
        )
    else:
        outcome_sd = st.number_input(
            "Outcome SD (standardized units)",
            min_value=0.01,
            value=1.0,
            step=0.1,
            help="The standard deviation of the outcome variable in standardized units. Default: 1.0.",
        )

    return {
        "n_timepoints_pre": n_timepoints_pre,
        "n_timepoints_post": n_timepoints_post,
        "autocorrelation": autocorrelation,
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
        engine_fn=compute_mdes_its,
    )

render()
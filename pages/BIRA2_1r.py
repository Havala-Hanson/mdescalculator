import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bira import compute_mdes_bira2_1r
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BIRA2_1r"
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
    # Blocked individual assignment structure
    # -----------------------------
    n_blocks = st.number_input(
        "Number of blocks (J)",
        min_value=2,
        value=20,
        step=1,
        help="Number of blocks (clusters) in the design. More blocks generally increase power, but with diminishing returns. Default: 20.",
    )

    n_individuals = st.number_input(
        "Total number of individuals (N)",
        min_value=4,
        value=200,
        step=10,
        help="Total number of individuals in the study (N). More individuals generally increase power. Default: 200.",
    )

    # -----------------------------
    # Random block structure
    # -----------------------------
    icc2 = st.number_input(
        "ICC at block level (ρ₂)",
        min_value=0.0,
        max_value=0.99,
        value=0.10,
        step=0.01,
        help="Intraclass correlation coefficient (ICC) at the block level. Higher ICC indicates more similarity within blocks, which can decrease power. Default: 0.10.",
    )

    omega2 = st.number_input(
        "Proportion of block-level variance in treatment contrast (ω₂)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
        help="Proportion of block-level variance that is in the treatment contrast. Higher values indicate more treatment effect heterogeneity at the block level, which can increase power. Default: 1.0.",
    )

    # -----------------------------
    # Covariates
    # -----------------------------
    r2_level1 = st.number_input(
        "R² (individual-level covariates, r²₁)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of individual-level variance explained by individual-level covariates. More explained variance can increase power. Default: 0.0.",

    )

    r2_level2 = st.number_input(
        "R² (block-level covariates, r²_{t2})",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of block-level variance explained by block-level covariates. More explained variance can increase power. Default: 0.0.",
    )

    # -----------------------------
    # Treatment allocation & reliability
    # -----------------------------
    prop_treated = st.number_input(
        "Proportion assigned to treatment (p)",
        min_value=0.05,
        max_value=0.95,
        value=0.50,
        step=0.05,
        help="Proportion of individuals assigned to the treatment group. Higher values indicate a larger treatment effect, which can increase the required sample size. Default: 0.50.",
    )

    rel1 = st.number_input(
        "Reliability of individual-level outcome (rel₁)",
        min_value=0.10,
        max_value=1.00,
        value=1.00,
        step=0.05,
        help="Reliability of the individual-level outcome measure. Higher reliability means less measurement error, which can increase power. Default: 1.00 (perfect reliability).",
    )

    # -----------------------------
    # Outcome type
    # -----------------------------
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

    # -----------------------------
    # Return engine inputs
    # -----------------------------
    return {
        "n_individuals": n_individuals,
        "n_blocks": n_blocks,
        "icc2": icc2,
        "omega2": omega2,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "alpha": alpha,
        "power": power,
        "two_tailed": two_tailed,
        "outcome_type": outcome_type,
        "baseline_prob": baseline_prob,
        "outcome_sd": outcome_sd,
        "prop_treated": prop_treated,
        "rel1": rel1,
    }


def render():
    render_calculator_page(
        design=design,
        input_render_fn=render_inputs,
        engine_fn=compute_mdes_bira2_1r,
        sensitivity_fields=["n_individuals", "n_blocks", "icc2", "omega2", "r2_level1", "r2_level2"],
    )

render()
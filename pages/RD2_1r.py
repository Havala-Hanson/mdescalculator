import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.rd import compute_mdes_rd
from services.calculator_template import render_calculator_page


DESIGN_CODE = "RD2_1r"
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
        help = "The significance level (α) is the threshold for rejecting the null hypothesis. A common choice is 0.05, which means there is a 5% chance of a Type I error (incorrectly rejecting the null when it is true). You can choose a more stringent level (e.g., 0.01) to reduce the risk of false positives, or a less stringent level (e.g., 0.10) if you are willing to accept more false positives in exchange for higher power.",
    )

    power = st.number_input(
        "Power (1 - β)",
        min_value=0.50,
        max_value=0.99,
        value=0.80,
        step=0.05,
        help = "Power is the probability of correctly rejecting the null hypothesis when there is a true effect. A common choice is 0.80, which means there is an 80% chance of detecting an effect if it exists. You can choose a higher power (e.g., 0.90) to increase the likelihood of detecting true effects, but this will also increase the required sample size.",
    )

    two_tailed = st.radio(
        "Two-tailed or one-tailed test?",
        options=[True, False],
        format_func=lambda x: "Two‑tailed" if x else "One‑tailed",
        index=0,
        help = "Two-tailed tests are more conservative and test for effects in both directions. One-tailed tests have more power to detect an effect in a specified direction but cannot detect effects in the opposite direction. Default: Two-tailed.",
    )

    # -----------------------------
    # Running variable and cutoff
    # -----------------------------
    cutoff = st.number_input(
        "Cutoff value",
        value=0.0,
        step=0.1,
        help = "The cutoff value is the threshold on the running variable that determines treatment assignment. Individuals with running variable values above (or below, depending on treatment side) the cutoff receive treatment, while those on the other side do not. Default: 0.0.",
    )

    bandwidth = st.number_input(
        "Bandwidth (h)",
        min_value=0.01,
        value=1.0,
        step=0.1,
        help = "The bandwidth (h) determines the range of the running variable around the cutoff that is included in the analysis. A smaller bandwidth focuses on observations closer to the cutoff, which can reduce bias but also reduces sample size and power. A larger bandwidth includes more observations, increasing power but potentially introducing bias if the relationship between the running variable and outcome is not well-modeled. Default: 1.0.",
    )

    # -----------------------------
    # Kernel choice
    # -----------------------------
    kernel = st.selectbox(
        "Kernel",
        ["triangular", "uniform", "epanechnikov"],
        index=0,
        help = "The kernel determines how observations are weighted based on their distance from the cutoff. 'Triangular' gives more weight to observations closer to the cutoff, 'Uniform' gives equal weight to all observations within the bandwidth, and 'Epanechnikov' gives more weight to observations near the cutoff but less than the triangular kernel. Default: Triangular.",
    )

    # -----------------------------
    # Treatment side
    # -----------------------------
    treatment_side = st.selectbox(
        "Treatment side",
        ["right", "left"],
        index=0,
        help = "Indicates which side of the cutoff receives treatment. 'Right' means individuals with running variable values above the cutoff are treated, while 'Left' means individuals with running variable values below the cutoff are treated. Default: Right.",
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
        help = "Proportion of variance in outcome explained by individual-level covariates. Default: 0.0.",
    )

    r2_level2 = st.number_input(
        "R² (level-2 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help = "Proportion of variance in outcome explained by level-2 covariates. In a standard RDD with fixed effects for bins of the running variable, level-2 covariates are absorbed by the fixed effects, so this is typically set to 0.0.",
    )

    # -----------------------------
    # Outcome type
    # -----------------------------
    outcome_type = st.selectbox(
        "Outcome type",
        ["continuous", "binary"],
        index=0,
        help = "The outcome type determines how the MDES is interpreted. 'Continuous' means the outcome is a continuous variable (e.g., income, test scores), while 'Binary' means the outcome is a binary variable (e.g., 0/1, yes/no). Default: Continuous.",
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
            help = "Baseline probability is the expected probability of the outcome occurring in the control group at the cutoff. This is used to convert the standardized MDES into an odds ratio or risk difference. If you don't have an estimate, you can use 0.50, and the MDES will be interpreted as the effect size needed to move from a 50% baseline probability to a higher or lower probability.",
        )
    else:
        outcome_sd = st.number_input(
            "Outcome SD (standardized units)",
            min_value=0.01,
            value=1.0,
            step=0.1,
            help = "Standard deviation of the outcome variable in standardized units (e.g., standard deviations from the mean). This is used to convert the standardized MDES into raw units. If you don't have an estimate, you can use 1.0, and the MDES will be interpreted in standard deviation units.",
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
        "two_tailed": two_tailed,
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
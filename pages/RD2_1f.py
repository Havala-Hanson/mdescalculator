import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.rd import compute_mdes_rd
from services.calculator_template import render_calculator_page


DESIGN_CODE = "RD2_1f"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
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

    # Level‑2 covariates are absorbed by fixed effects
    r2_level2 = 0.0

    # -----------------------------
    # Outcome type
    # -----------------------------
    outcome_type = st.selectbox(
        "Outcome type",
        ["continuous", "binary"],
        index=0,
        help = "The type of outcome variable you are planning to analyze. 'Continuous' means the outcome is measured on a continuous scale (e.g., test scores, income), while 'Binary' means the outcome is dichotomous (e.g., success/failure, yes/no). This choice affects how the MDES is interpreted and how the power analysis is conducted. Default: Continuous.",
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
        help="Power is the probability of correctly rejecting the null hypothesis when the alternative hypothesis is true. Higher power means a lower chance of a Type II error (failing to detect a true effect). Default: 0.80.",
    )

    two_tailed = st.radio(
        "Two-tailed or one-tailed test?",
        options=[True, False],
        format_func=lambda x: "Two‑tailed" if x else "One‑tailed",
        index=0,
        help= "Two-tailed tests are more conservative and test for effects in both directions. One-tailed tests have more power to detect an effect in a specified direction but cannot detect effects in the opposite direction. Default: Two-tailed.",
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
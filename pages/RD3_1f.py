import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.rd import compute_mdes_rd
from services.calculator_template import render_calculator_page


DESIGN_CODE = "RD3_1f"
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
        help = "The significance level (α) is the probability of a Type I error (false positive) (i.e., the threshold for rejecting the null hypothesis). Common values are 0.05 (5% significance level) or 0.01 (1% significance level). Lower α requires stronger evidence to reject the null hypothesis, which typically increases required sample sizes.",
    )

    power = st.number_input(
        "Power (1 - β)",
        min_value=0.50,
        max_value=0.99,
        value=0.80,
        step=0.05,
        help = "Power is the probability of correctly rejecting the null hypothesis when there is a true effect. Common values are 0.80 (80% power) or 0.90 (90% power). Higher power requires larger sample sizes
    )

    two_tailed = st.radio(
        "Two-tailed or one-tailed test?",
        options=[True, False],
        format_func=lambda x: "Two‑tailed" if x else "One‑tailed",
        index=0,
        help = "Two-tailed tests are more conservative and test for effects in both directions. One-tailed tests have more power to detect an effect in a specified direction but cannot detect effects in the opposite direction. Default: Two-tailed.",
    )
    
    # -----------------------------
    # Running variable structure
    # -----------------------------
    cutoff = st.number_input(
        "Cutoff value",
        value=0.0,
        step=0.1,
        help = "The cutoff value on the running variable that determines treatment assignment. Units should be in the same scale as the running variable. Default: 0.0.",
    )

    bandwidth = st.number_input(
        "Bandwidth (h)",
        min_value=0.01,
        value=1.0,
        step=0.1,
        help = "The bandwidth (h) is the range of the running variable around the cutoff that is used for the analysis. Units should be in the same scale as the running variable. A smaller bandwidth focuses on observations closer to the cutoff, which can reduce bias but also reduces sample size and power. A larger bandwidth includes more observations, increasing power but potentially introducing bias if the relationship between the running variable and outcome is not well-modeled. Default: 1.0.",
    )

    kernel = st.selectbox(
        "Kernel",
        ["triangular", "uniform", "epanechnikov"],
        index=0,
        help = "The kernel function determines how observations are weighted based on their distance from the cutoff. 'Triangular' gives more weight to observations closer to the cutoff, 'Uniform' gives equal weight to all observations within the bandwidth, and 'Epanechnikov' gives more weight to observations near the cutoff but less than the triangular kernel. Default: Triangular.",
    )

    treatment_side = st.selectbox(
        "Treatment side",
        ["right", "left"],
        index=0,
        help = "The side of the cutoff that receives treatment. 'Right' means that observations with running variable values above the cutoff receive treatment, while 'Left' means that observations with running variable values below the cutoff receive treatment. Default: Right.",
    )

    # -----------------------------
    # Covariates
    # -----------------------------
    r2_level1 = st.number_input(
        "R² (level-1 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help = "Proportion of variance in the outcome explained by level-1 (individual-level) covariates. This can increase power by reducing residual variance. Default: 0.0.",
    )

    r2_level2 = st.number_input(
        "R² (level-2 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help = "Proportion of variance in the outcome explained by level-2 (cluster-level) covariates. This can increase power by reducing residual variance at the cluster level. Default: 0.0.",
    )

    # Level-3 covariates absorbed by fixed effects
    r2_level3 = 0.0

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

    return {
        "cutoff": cutoff,
        "bandwidth": bandwidth,
        "kernel": kernel,
        "treatment_side": treatment_side,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "r2_level3": r2_level3,
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
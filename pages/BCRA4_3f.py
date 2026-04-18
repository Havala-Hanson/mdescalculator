# pages/BCRA4_3f.py

import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.mdes_four_level import compute_mdes_bcra4_3f
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BCRA4_3f"
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
    # Four-level structure
    # -----------------------------
    n_level4 = st.number_input(
        "Number of level-4 blocks (K)",
        min_value=1,
        value=20,
        step=1,
        help="Number of level-4 blocks (e.g., schools, clinics). More blocks generally increase power, but with diminishing returns. Default: 20.",
    )

    n_level3 = st.number_input(
        "Number of level-3 units per block (L3 per L4)",
        min_value=3,
        value=5,
        step=1,
        help="Number of level-3 units (e.g., classrooms, departments) nested within each level-4 block. More level-3 units can increase power, especially when there is substantial level-3 variance. Default: 5.",
    )

    n_level2 = st.number_input(
        "Number of level-2 units per level-3 unit (L2 per L3)",
        min_value=1,
        value=5,
        step=1,
        help="Number of level-2 units (e.g., students, patients) nested within each level-3 unit. More level-2 units can increase power, especially when there is substantial level-2 variance. Default: 5.",
    )

    cluster_size = st.number_input(
        "Average number of level-1 units per level-2 unit (n)",
        min_value=1,
        value=30,
        step=1,
        help="Average number of level-1 units (e.g., test scores, measurements) nested within each level-2 unit. More level-1 units can increase power, especially when there is substantial level-1 variance. Default: 30.",
    )

    p_treat = st.number_input(
        "Treatment allocation ratio (p)",
        min_value=0.05,
        max_value=0.95,
        value=0.5,
        step=0.05,
        help="Proportion of level-3 units assigned to treatment within each block. Higher values indicate a more imbalanced design, which can increase the required sample size. Default: 0.5 (balanced).",
    )

    # -----------------------------
    # ICCs
    # -----------------------------
    icc4 = st.number_input(
        "ICC (level 4)",
        min_value=0.0,
        max_value=0.99,
        value=0.02,
        step=0.01,
        help="Intraclass correlation coefficient at level 4 (e.g., schools, clinics). Higher values indicate more similarity within blocks, which can increase the required sample size. Default: 0.02.",
    )


    icc3 = st.number_input(
        "ICC (level 3)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
        help="Intraclass correlation coefficient at level 3 (e.g., classrooms, departments). Higher values indicate more similarity within level-3 units, which can increase the required sample size. Default: 0.05.",
    )

    icc2 = st.number_input(
        "ICC (level 2)",
        min_value=0.0,
        max_value=0.99,
        value=0.10,
        step=0.01,
        help="Intraclass correlation coefficient at level 2 (e.g., students, patients). Higher values indicate more similarity within level-2 units, which can increase the required sample size. Default: 0.10.",
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
        help="Proportion of level-1 variance explained by level-1 covariates. More explained variance can increase power. Default: 0.0.",
    )

    r2_level2 = st.number_input(
        "R² (level-2 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of level-2 variance explained by level-2 covariates. More explained variance can increase power. Default: 0.0.",
    )

    r2_level3 = st.number_input(
        "R² (level-3 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of level-3 variance explained by level-3 covariates. More explained variance can increase power. Default: 0.0.",
    )

    g3 = st.number_input(
        "Number of level-3 covariates (g₃)",
        min_value=0,
        value=0,
        step=1,
        help="Number of level-3 covariates used in the model. Reduces degrees of freedom: df = L·(K − 2) − g₃. More covariates can increase power but also reduce degrees of freedom. Default: 0.",

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
        "n_level4": n_level4,
        "n_level3": n_level3,
        "n_level2": n_level2,
        "cluster_size": cluster_size,
        "p_treat": p_treat,
        "icc4": icc4,
        "icc3": icc3,
        "icc2": icc2,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "r2_level3": r2_level3,
        "g3": g3,
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
        engine_fn=compute_mdes_bcra4_3f,
        sensitivity_fields=["n_level4", "n_level3", "n_level2", "cluster_size", "icc2", "icc3", "icc4", "r2_level1", "r2_level2", "r2_level3"],
    )

render()
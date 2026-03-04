# pages/cra2_2r.py

import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.cra import compute_mdes_cra
from services.calculator_template import render_calculator_page


DESIGN_CODE = "CRA2_2r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    
    # -----------------------------
    # Test settings
    # -----------------------------
    p_treat = st.number_input(
        "Treatment proportion (p)",
        min_value=0.01,
        max_value=0.99,
        value=0.50,
        step=0.01,
        help="Proportion of clusters assigned to treatment. R default: 0.50.",
    )

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
    # Cluster structure
    # -----------------------------
    n_clusters = st.number_input(
        "Number of clusters (J)",
        min_value=3,
        value=20,
        step=1,
    )

    cluster_size = st.number_input(
        "Average cluster size (n)",
        min_value=1,
        value=30,
        step=1,
    )

    # -----------------------------
    # ICC and covariates
    # -----------------------------
    icc = st.number_input(
        "Intraclass correlation (ICC)",
        min_value=0.0,
        max_value=0.99,
        value=0.10,
        step=0.01,
    )

    r2_level1 = st.number_input(
        "R² (individual-level covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
    )

    r2_level2 = st.number_input(
        "R² (cluster-level covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
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
        )
    else:
        outcome_sd = st.number_input(
            "Outcome SD (raw units)",
            min_value=0.01,
            value=1.0,
            step=0.1,
        )

    rel1 = st.number_input(
        "Outcome reliability (rel1)",
        min_value=0.01,
        max_value=1.00,
        value=1.00,
        step=0.01,
        help="Reliability of the level-1 outcome measure. R default: 1.0 (perfect reliability).",
    )

    # -----------------------------
    # Return engine inputs
    # -----------------------------
    return {
        "n_clusters": n_clusters,
        "cluster_size": cluster_size,
        "icc": icc,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "p_treat": p_treat,
        "rel1": rel1,
        "two_tailed": two_tailed,
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
        engine_fn=compute_mdes_cra,
    )

render()
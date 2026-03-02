# pages/cra2_2r.py

import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.cra import compute_mdes_cra
from services.calculator_template import render_calculator_page


DESIGN_CODE = "CRA2_2r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):
    # -----------------------------
    # Cluster structure
    # -----------------------------
    n_clusters = st.number_input(
        "Number of clusters (J)",
        min_value=3,
        value=design.defaults.get("n_clusters", 20),
        step=1,
    )

    cluster_size = st.number_input(
        "Average cluster size (n)",
        min_value=1,
        value=design.defaults.get("cluster_size", 30),
        step=1,
    )

    # -----------------------------
    # ICC and covariates
    # -----------------------------
    icc = st.number_input(
        "Intraclass correlation (ICC)",
        min_value=0.0,
        max_value=0.99,
        value=design.defaults.get("icc", 0.10),
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

    # -----------------------------
    # Test settings
    # -----------------------------
    two_tailed = st.checkbox(
        "Two-tailed test",
        value=True,
    )

    p_treat = st.number_input(
        "Treatment proportion (p)",
        min_value=0.01,
        max_value=0.99,
        value=0.50,
        step=0.01,
        help="Proportion of clusters assigned to treatment. R default: 0.50.",
    )

    rel1 = st.number_input(
        "Outcome reliability (rel1)",
        min_value=0.01,
        max_value=1.00,
        value=1.00,
        step=0.01,
        help="Reliability of the level-1 outcome measure. R default: 1.0 (perfect reliability).",
    )

    alpha = st.number_input(
        "Significance level (α)",
        min_value=0.001,
        max_value=0.20,
        value=0.05,
        step=0.01,
    )

    power = st.number_input(
        "Power (1 - β)",
        min_value=0.50,
        max_value=0.99,
        value=0.80,
        step=0.05,
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
import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bira import compute_mdes_bira3_1r
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BIRA3_1r"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design):

    # ------------------------------------------------------------
    # Three-level sample structure
    # ------------------------------------------------------------
    n_blocks = st.number_input(
        "Number of level‑3 blocks (K)",
        min_value=2,
        value=20,
        step=1,
    )

    n_clusters_per_block = st.number_input(
        "Clusters per block (J)",
        min_value=1,
        value=5,
        step=1,
    )

    cluster_size = st.number_input(
        "Individuals per cluster (n)",
        min_value=2,
        value=20,
        step=1,
    )

    # ------------------------------------------------------------
    # ICCs
    # ------------------------------------------------------------
    icc3 = st.number_input(
        "ICC at block level (ρ₃)",
        min_value=0.0,
        max_value=0.99,
        value=0.05,
        step=0.01,
    )

    icc2 = st.number_input(
        "ICC at cluster level (ρ₂)",
        min_value=0.0,
        max_value=0.99,
        value=0.10,
        step=0.01,
    )

    # ------------------------------------------------------------
    # Treatment‑explained variance (omegas)
    # ------------------------------------------------------------
    omega3 = st.number_input(
        "ω₃ (treatment share of level‑3 variance)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
    )

    omega2 = st.number_input(
        "ω₂ (treatment share of level‑2 variance)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
    )

    # ------------------------------------------------------------
    # Covariate R²
    # ------------------------------------------------------------
    r2_level1 = st.number_input("R² level 1 (r₂₁)", 0.0, 0.99, 0.0, 0.05)
    r2_level2 = st.number_input("R² level 2 (r₂t₂)", 0.0, 0.99, 0.0, 0.05)
    r2_level3 = st.number_input("R² level 3 (r₂t₃)", 0.0, 0.99, 0.0, 0.05)

    # ------------------------------------------------------------
    # Outcome type
    # ------------------------------------------------------------
    outcome_type = st.selectbox("Outcome type", ["continuous", "binary"], index=0)

    baseline_prob = None
    outcome_sd = None
    if outcome_type == "binary":
        baseline_prob = st.number_input("Baseline probability", 0.01, 0.99, 0.50, 0.01)
    else:
        outcome_sd = st.number_input("Outcome SD (raw units)", 0.01, value=1.0, step=0.1)

    # ------------------------------------------------------------
    # Test settings
    # ------------------------------------------------------------
    prop_treated = st.number_input("Proportion treated (p)", 0.05, 0.95, 0.50, 0.05)
    alpha = st.number_input("Significance level (α)", 0.001, 0.20, 0.05, 0.01)
    power = st.number_input("Power (1 − β)", 0.50, 0.99, 0.80, 0.05)

    return {
        "n_blocks": n_blocks,
        "n_clusters_per_block": n_clusters_per_block,
        "cluster_size": cluster_size,
        "icc2": icc2,
        "icc3": icc3,
        "omega2": omega2,
        "omega3": omega3,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "r2_level3": r2_level3,
        "alpha": alpha,
        "power": power,
        "outcome_type": outcome_type,
        "baseline_prob": baseline_prob,
        "outcome_sd": outcome_sd,
        "prop_treated": prop_treated,
    }


def render():
    render_calculator_page(
        design=design,
        input_render_fn=render_inputs,
        engine_fn=compute_mdes_bira3_1r,
    )
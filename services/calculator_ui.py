import streamlit as st
import math

# ---------------------------------------------------------------------
# Read initial state
# ---------------------------------------------------------------------

from services.prepopulate import prepopulate_for_design
import streamlit as st

def read_initial_state(design):
    prepopulate_for_design(design, st.session_state)
    return st.session_state

# ---------------------------------------------------------------------
# Header + statistical background
# ---------------------------------------------------------------------

import re

def render_header(design):
    hdr = design.calculator_header

    st.title(f"{hdr['icon']} {hdr['title']}")
    st.subheader(hdr["subtitle"])
    st.markdown(hdr["description"])

    with st.expander("📖 Statistical background"):
        bg = design.calculator_background

        # Auto-wrap bare formulas
        if not re.search(r"\${1,2}.*\${1,2}", bg):
            bg = f"$$\n{bg}\n$$"

        st.markdown(bg, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Input renderers
# ---------------------------------------------------------------------

from services.dynamic_labels import dynamic_label
from config.input_descriptions import INPUT_DESCRIPTIONS

def render_input(field, state, design):
    """
    Render a single calculator input with:
    - dynamic label based on design structure
    - caption (short definition)
    - tooltip (practical example)
    - value stored back into session_state
    """

    # Dynamic label based on design structure
    label = dynamic_label(field, design)

    # Metadata for caption + tooltip
    meta = INPUT_DESCRIPTIONS.get(field, {})
    caption = meta.get("caption", "")
    tooltip = meta.get("tooltip", "")

    # Render the input
    value = st.number_input(
        label,
        value=state.get(field, 0),
        help=tooltip,
        key=field,  # ensures Streamlit manages the widget cleanly
    )

    # Caption under the input
    if caption:
        st.caption(caption)

    # Store updated value
    state[field] = value

# ---------------------------------------------------------------------
# Sample size inputs (supports all families)
# ---------------------------------------------------------------------

def render_sample_inputs(design, state):
    fields = design.calculator_config.get("sample_fields", [])
    if not fields:
        return

    st.subheader("Sample Size")

    for field in fields:
        render_input(field, state, design)

# ---------------------------------------------------------------------
# ICC & covariate inputs
# ---------------------------------------------------------------------

def render_icc_covariate_inputs(design, state):
    icc_fields = design.calculator_config.get("icc_fields", [])
    cov_fields = design.calculator_config.get("covariate_fields", [])

    if not icc_fields and not cov_fields:
        return

    st.subheader("ICC and Covariates")

    for field in icc_fields + cov_fields:
        render_input(field, state, design)

# ---------------------------------------------------------------------
# Block-level inputs (if applicable)
# ---------------------------------------------------------------------

def render_block_inputs(design, state):
    fields = design.calculator_config.get("block_fields", [])
    if not fields:
        return

    st.subheader("Blocking")

    for field in fields:
        render_input(field, state, design)

# ---------------------------------------------------------------------
# Cluster-level inputs (if applicable)
# ---------------------------------------------------------------------
def render_cluster_inputs(design, state):
    fields = design.calculator_config.get("cluster_fields", [])
    if not fields:
        return

    st.subheader("Cluster Structure")

    for field in fields:
        render_input(field, state, design)

# ---------------------------------------------------------------------
# RD-specific inputs (if applicable)
# ---------------------------------------------------------------------

def render_rd_inputs(design, state):
    fields = design.calculator_config.get("rd_fields", [])
    if not fields:
        return

    st.subheader("Regression Discontinuity Inputs")

    for field in fields:
        render_input(field, state, design)

# ---------------------------------------------------------------------
# ITS-specific inputs (if applicable)
# ---------------------------------------------------------------------

def render_its_inputs(design, state):
    fields = design.calculator_config.get("its_fields", [])
    if not fields:
        return

    st.subheader("Time Series Structure")

    for field in fields:
        render_input(field, state, design)

# ---------------------------------------------------------------------
# Test settings
# ---------------------------------------------------------------------

def render_test_settings(design, state):
    st.subheader("Test Settings")

    # Always render alpha and power using the unified input renderer
    for field in ["alpha", "power"]:
        render_input(field, state, design)

# ---------------------------------------------------------------------
# Outcome-type inputs
# ---------------------------------------------------------------------

def render_outcome_type_inputs(design, state):
    st.subheader("Outcome Type")

    # Choose outcome type
    outcome_type = st.radio(
        "Outcome type",
        options=["continuous", "binary"],
        index=0 if state.get("outcome_type", "continuous") == "continuous" else 1,
        horizontal=True,
    )

    # Store outcome type
    state["outcome_type"] = outcome_type

    # Clean irrelevant state
    if outcome_type == "binary":
        state["outcome_sd_input"] = None
    else:
        state["baseline_prob"] = None

    # Binary outcome
    if outcome_type == "binary":
        baseline_prob = st.slider(
            "Baseline event probability",
            min_value=0.01,
            max_value=0.99,
            value=state.get("baseline_prob", 0.50),
            step=0.01,
            format="%.2f",
        )
        state["baseline_prob"] = baseline_prob
        state["outcome_sd"] = math.sqrt(baseline_prob * (1 - baseline_prob))
        return

    # Continuous outcome
    outcome_sd_input = st.number_input(
        "Outcome SD (optional)",
        min_value=0.0,
        value=state.get("outcome_sd_input", 1.0),
        step=0.1,
    )
    state["outcome_sd_input"] = outcome_sd_input
    state["outcome_sd"] = outcome_sd_input if outcome_sd_input > 0 else None

# ---------------------------------------------------------------------
# Results rendering
# ---------------------------------------------------------------------

def render_results(result):
    if result is None:
        return

    st.subheader("Results")

    st.metric("MDES (standardized)", f"{result.mdes:.4f}")
    st.metric("Standard error (σ₍δ₎)", f"{result.se:.4f}")
    st.metric("Degrees of freedom", f"{result.df}")
    st.metric("Design effect (DEFF)", f"{result.design_effect:.3f}")
    st.metric("Effective sample size", f"{result.effective_n:,.1f}")
    st.metric("Total sample size", f"{result.total_n}")

    if result.mdes_pct_points is not None:
        st.metric("MDES (percentage points)", f"{result.mdes_pct_points:.2f} pp")

    if result.mdes_raw is not None:
        st.metric("MDES (raw units)", f"{result.mdes_raw:.4f}")

    st.markdown("### Interpretation")
    st.write(result.interpretation)
    
# ---------------------------------------------------------------------
# Top-level calculator assembly
# ---------------------------------------------------------------------

def render_calculator_page(design):
    state = read_initial_state(design)

    # Header + background
    render_header(design)

    st.markdown("---")

    # Outcome type first (because it affects SD logic)
    render_outcome_type_inputs(design, state)

    st.markdown("---")

    # Sample size inputs
    render_sample_inputs(design, state)

    # ICC + covariates
    render_icc_covariate_inputs(design, state)

    # Blocking (if applicable)
    if design.calculator_config.get("block_fields"):
        render_block_inputs(design, state)

    # Cluster structure (if applicable)
    if design.calculator_config.get("cluster_fields"):
        render_cluster_inputs(design, state)

    # RD inputs (if applicable)
    if design.calculator_config.get("rd_fields"):
        render_rd_inputs(design, state)

    # ITS inputs (if applicable)
    if design.calculator_config.get("its_fields"):
        render_its_inputs(design, state)

    # Test settings (alpha + power)
    render_test_settings(design, state)

    st.markdown("---")

    # Run engine
    if st.button("Compute MDES"):
        inputs = collect_engine_inputs(design, state)
        result = run_engine(design, inputs)
        render_results(result)
        render_download_button(result, state, design.calculator_header["title"], design)

# ---------------------------------------------------------------------
# Collect engine inputs
# ---------------------------------------------------------------------

def collect_engine_inputs(design, state):
    cfg = design.calculator_config
    inputs = {}

    # Sample fields
    for field in cfg.get("sample_fields", []):
        if field in state:
            inputs[field] = state[field]

    # ICC fields
    for field in cfg.get("icc_fields", []):
        if field in state:
            inputs[field] = state[field]

    # Covariate fields
    for field in cfg.get("covariate_fields", []):
        if field in state:
            inputs[field] = state[field]

    # Block fields
    for field in cfg.get("block_fields", []):
        if field in state:
            inputs[field] = state[field]

    # Cluster fields
    for field in cfg.get("cluster_fields", []):
        if field in state:
            inputs[field] = state[field]

    # RD fields
    for field in cfg.get("rd_fields", []):
        if field in state:
            inputs[field] = state[field]

    # ITS fields
    for field in cfg.get("its_fields", []):
        if field in state:
            inputs[field] = state[field]

    # Test settings (always alpha + power)
    for field in ["alpha", "power"]:
        if field in state:
            inputs[field] = state[field]

    # Outcome-type fields
    inputs["outcome_type"] = state.get("outcome_type")
    inputs["baseline_prob"] = state.get("baseline_prob")
    inputs["outcome_sd"] = state.get("outcome_sd")

    return inputs

# ---------------------------------------------------------------------
# Run engine 
# ---------------------------------------------------------------------
from mdes_engines.ira import compute_mdes_ira
from mdes_engines.bira import compute_mdes_bira
from mdes_engines.cra import compute_mdes_cra
from mdes_engines.bcra import compute_mdes_bcra
from mdes_engines.rd import compute_mdes_rd
from mdes_engines.its import compute_mdes_its

ENGINE_MAP = {
    "compute_mdes_ira": compute_mdes_ira,
    "compute_mdes_bira": compute_mdes_bira,
    "compute_mdes_cra": compute_mdes_cra,
    "compute_mdes_bcra": compute_mdes_bcra,
    "compute_mdes_rd": compute_mdes_rd,
    "compute_mdes_its": compute_mdes_its,

} 

def run_engine(design, inputs):
    engine_name = design.calculator_config.get("engine")
    if engine_name is None:
        raise ValueError(f"No engine defined for design {design.code}")

    engine = ENGINE_MAP.get(engine_name)
    if engine is None:
        raise ValueError(f"Engine '{engine_name}' not found in ENGINE_MAP")

    return engine(**inputs)


# ---------------------------------------------------------------------
# Download block
# ---------------------------------------------------------------------

def render_download_button(result, state, design_title, design):
    if result is None:
        return

    st.subheader("⬇️ Download results")

    cfg = design.calculator_config

    # Collect only fields relevant to this design
    ordered_fields = (
        cfg.get("sample_fields", [])
        + cfg.get("icc_fields", [])
        + cfg.get("covariate_fields", [])
        + cfg.get("block_fields", [])
        + cfg.get("cluster_fields", [])
        + cfg.get("rd_fields", [])
        + cfg.get("its_fields", [])
        + ["alpha", "power"]
    )

    summary_lines = [
        f"MDES Calculator – {design_title}",
        "=" * (20 + len(design_title)),
        "",
        "Inputs",
        "-" * 45,
    ]

    # Add inputs in a clean, design-specific order
    for field in ordered_fields:
        if field in state:
            summary_lines.append(f"{field}: {state[field]}")

    # Outcome-type-specific
    summary_lines.append(f"outcome_type: {state.get('outcome_type')}")

    if state.get("outcome_type") == "binary":
        summary_lines.append(f"baseline_prob: {state.get('baseline_prob')}")
        summary_lines.append(f"outcome_sd: {state.get('outcome_sd')}")
    else:
        sd = state.get("outcome_sd_input")
        if sd is not None:
            summary_lines.append(f"outcome_sd_input: {sd}")
        summary_lines.append(f"outcome_sd: {state.get('outcome_sd')}")

    summary_lines += [
        "",
        "Results",
        "-" * 45,
        f"MDES (standardized):           {result.mdes:.4f}",
        f"Standard error (sigma_delta):  {result.se:.4f}",
        f"Degrees of freedom:            {result.df}",
        f"Design effect (DEFF):          {result.design_effect:.3f}",
        f"Effective sample size:         {result.effective_n:,.1f}",
        f"Total sample size:             {result.total_n}",
    ]

    if result.mdes_pct_points is not None:
        summary_lines.append(
            f"MDES (percentage points):      {result.mdes_pct_points:.2f} pp"
        )

    if result.mdes_raw is not None:
        summary_lines.append(
            f"MDES (raw units):              {result.mdes_raw:.4f}"
        )

    summary_lines += ["", result.interpretation]

    summary_text = "\n".join(summary_lines)

    st.download_button(
        label="Download summary (TXT)",
        data=summary_text,
        file_name="mdes_results.txt",
        mime="text/plain",
    )
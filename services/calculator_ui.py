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

def render_header(design):
    hdr = design.calculator_header

    st.title(f"{hdr['icon']} {hdr['title']}")
    st.subheader(hdr["subtitle"])
    st.write(hdr["description"])

    with st.expander("📖 Statistical background"):
        st.markdown(design.calculator_background)


# ---------------------------------------------------------------------
# Sample size inputs (supports all families)
# ---------------------------------------------------------------------

def render_sample_inputs(design, state):
    cfg = design.calculator_config["sample_inputs"]
    out = {}

    for field in cfg["fields"]:
        rec = cfg["recommended"].get(field)
        default = state[field]

        # Cluster-level fields
        if field == "n_clusters":
            out[field] = st.number_input(
                "Number of clusters (J)",
                min_value=3,
                max_value=10000,
                value=default,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        elif field == "cluster_size":
            out[field] = st.number_input(
                "Average cluster size (n)",
                min_value=1,
                max_value=10000,
                value=default,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        elif field == "n_blocks":
            out[field] = st.number_input(
                "Number of blocks (B)",
                min_value=1,
                max_value=10000,
                value=default,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        # Individual-level fields
        elif field == "n_individuals":
            out[field] = st.number_input(
                "Number of individuals (N)",
                min_value=10,
                max_value=1_000_000,
                value=default,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        # RD fields
        elif field == "n_units":
            out[field] = st.number_input(
                "Number of units (N)",
                min_value=100,
                max_value=1_000_000,
                value=default,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        elif field == "bandwidth":
            out[field] = st.slider(
                "Bandwidth (h)",
                min_value=0.01,
                max_value=5.0,
                value=default,
                step=0.01,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        elif field == "running_var_sd":
            out[field] = st.number_input(
                "Running variable SD",
                min_value=0.01,
                max_value=10.0,
                value=default,
                step=0.01,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        # ITS fields
        elif field == "n_timepoints_pre":
            out[field] = st.number_input(
                "Pre-intervention timepoints",
                min_value=1,
                max_value=200,
                value=default,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        elif field == "n_timepoints_post":
            out[field] = st.number_input(
                "Post-intervention timepoints",
                min_value=1,
                max_value=200,
                value=default,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        elif field == "autocorrelation":
            out[field] = st.slider(
                "Autocorrelation (ρ)",
                min_value=0.0,
                max_value=0.99,
                value=default,
                step=0.01,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        # Treatment proportion
        elif field == "p_treat":
            out[field] = st.slider(
                "Proportion treated (P)",
                min_value=0.1,
                max_value=0.9,
                value=default,
                step=0.05,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

    return out


# ---------------------------------------------------------------------
# ICC & covariate inputs
# ---------------------------------------------------------------------

def render_icc_covariate_inputs(design, state):
    cfg = design.calculator_config["icc_inputs"]
    out = {}

    for field in cfg["fields"]:
        rec = cfg["recommended"].get(field)
        default = state[field]

        if field == "icc":
            out[field] = st.slider(
                "Intraclass correlation (ρ)",
                min_value=0.0,
                max_value=0.5,
                value=default,
                step=0.01,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        elif field == "r2_level1":
            out[field] = st.slider(
                "Individual-level R² (R²₁)",
                min_value=0.0,
                max_value=0.99,
                value=default,
                step=0.01,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

        elif field == "r2_level2":
            out[field] = st.slider(
                "Cluster-level R² (R²₂)",
                min_value=0.0,
                max_value=0.99,
                value=default,
                step=0.01,
                help=f"Recommended range: {rec[0]}–{rec[1]}",
            )

    return out


# ---------------------------------------------------------------------
# Test settings
# ---------------------------------------------------------------------

def render_test_settings(state):
    alpha = st.selectbox(
        "Significance level (α)",
        options=[0.01, 0.05, 0.10],
        index=[0.01, 0.05, 0.10].index(state["alpha"]),
    )
    power = st.selectbox(
        "Statistical power (1 − β)",
        options=[0.70, 0.75, 0.80, 0.85, 0.90],
        index=[0.70, 0.75, 0.80, 0.85, 0.90].index(state["power"]),
    )
    return {"alpha": alpha, "power": power}


# ---------------------------------------------------------------------
# Outcome-type inputs
# ---------------------------------------------------------------------

def render_outcome_type_inputs(design, state):
    outcome_type = st.radio(
        "Outcome type",
        options=["continuous", "binary"],
        index=0 if state["outcome_type"] == "continuous" else 1,
        horizontal=True,
    )

    # Clean irrelevant state
    if outcome_type == "binary":
        st.session_state.outcome_sd_input = None
    else:
        st.session_state.baseline_prob = None

    if outcome_type == "binary":
        baseline_prob = st.slider(
            "Baseline event probability (p₀)",
            min_value=0.01,
            max_value=0.99,
            value=state.get("baseline_prob", 0.50),
            step=0.01,
            format="%.2f",
        )
        outcome_sd = math.sqrt(baseline_prob * (1 - baseline_prob))
        return {
            "outcome_type": "binary",
            "baseline_prob": baseline_prob,
            "outcome_sd": outcome_sd,
        }

    else:
        outcome_sd_input = st.number_input(
            "Outcome SD (optional)",
            min_value=0.0,
            value=state.get("outcome_sd_input", 1.0),
            step=0.1,
        )
        outcome_sd = outcome_sd_input if outcome_sd_input > 0 else None
        return {
            "outcome_type": "continuous",
            "baseline_prob": None,
            "outcome_sd": outcome_sd,
        }


# ---------------------------------------------------------------------
# Collect engine inputs
# ---------------------------------------------------------------------

def collect_engine_inputs(design, sample, icc_cov, test, outcome):
    cfg = design.calculator_config
    inputs = {}

    # Sample inputs
    for field in cfg["sample_inputs"]["fields"]:
        if field in sample:
            inputs[field] = sample[field]

    # ICC & covariates
    for field in cfg["icc_inputs"]["fields"]:
        if field in icc_cov:
            inputs[field] = icc_cov[field]

    # Test settings
    for field in cfg["test_settings"]["fields"]:
        if field in test:
            inputs[field] = test[field]

    # Outcome-type
    inputs["outcome_type"] = outcome["outcome_type"]
    inputs["baseline_prob"] = outcome["baseline_prob"]
    inputs["outcome_sd"] = outcome["outcome_sd"]

    # Treatment proportion (common)
    if "p_treat" in sample:
        inputs["p_treat"] = sample["p_treat"]

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
    engine_name = design.calculator_config["engine"]
    engine = ENGINE_MAP[engine_name]
    return engine(**inputs)


# ---------------------------------------------------------------------
# Download block
# ---------------------------------------------------------------------

def render_download_button(result, state, design_title):
    if result is None:
        return

    st.subheader("⬇️ Download results")

    summary_lines = [
        f"MDES Calculator – {design_title}",
        "=" * (20 + len(design_title)),
        "",
        "Inputs",
        "-" * 45,
    ]

    # Add state values
    for key, value in state.items():
        if key in ["outcome_sd_input", "baseline_prob", "outcome_type"]:
            continue
        summary_lines.append(f"{key}: {value}")

    # Outcome-type-specific
    if state.get("outcome_type") == "binary":
        summary_lines.append(f"baseline_prob: {state.get('baseline_prob')}")
    else:
        sd = state.get("outcome_sd_input")
        if sd is not None:
            summary_lines.append(f"outcome_sd_input: {sd}")

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
import streamlit as st
import math
import re 

from services.interpretation import interpret_mdes

# ---------------------------------------------------------------------
# Read initial state
# ---------------------------------------------------------------------

from services.prepopulate import prepopulate_for_design

def read_initial_state(design, outcome_type="continuous"):
    if (
        st.session_state.get("selected_design") != design.code
        or st.session_state.get("outcome_type") != outcome_type
    ):
        prepopulate_for_design(design, st.session_state, outcome_type=outcome_type)
    return st.session_state

# ---------------------------------------------------------------------
# Header + statistical background
# ---------------------------------------------------------------------
def render_header(design):
    hdr = design.calculator_header

    st.header(f"{hdr['icon']} {hdr['title']}")
    st.subheader(hdr["subtitle"])
    st.markdown(hdr["description"])
    
    with st.expander("Statistical background"):
        st.markdown(
            "**Structure:**  Three levels: individuals (1) within clusters (2) within blocks (3). "
            "Clusters are randomized within blocks; block effects are fixed. Assignment at level 2.\n\n"
            "**Key formulas:**\n\n")
        st.markdown(r"- **Variance**")
        
        st.latex(
            r"""
            \operatorname{Var}(\hat{\delta}) =
            \left[
            \frac{\rho_2(1 - R^2_2)}{P(1-P)\,K\,J}
            + \frac{(1 - \rho_2)(1 - R^2_1)}{P(1-P)\,K\,J\,n}
            \right]
            \cdot \frac{K}{K - 1}
            """
        )
        st.markdown("- **Degrees of freedom:**")
        st.latex(r"\text{df} = K(J - 1) - 1")

        st.markdown("- **Adjustment for covariates:** R-squrared for levels 1 and 2 reduce between- and within-cluster variance; with the finite-block correction:")
        st.latex(r"\frac{K}{K-1}")
        




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
    for field in ["alpha", "power", "two-tailed"]:
        render_input(field, state, design)

# ---------------------------------------------------------------------
# Outcome-type inputs
# ---------------------------------------------------------------------

def render_outcome_type_inputs(state):
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

# ---------------------------------------------------------------------
# Results rendering
# ---------------------------------------------------------------------

def render_results(result, state):
    if result is None:
        return

    st.subheader("Results")

    outcome_type = state.get("outcome_type")

    # For continuous outcomes, show standardized MDES once.
    # For binary outcomes, show standardized MDES (if available) and percentage points.
    if outcome_type == "continuous":
        st.metric("MDES (standardized)", f"{result.mdes:.4f}")
    else:
        st.metric("MDES (standardized)", f"{result.mdes:.4f}")
        st.metric("MDES (percentage points)", f"{result.mdes_pct_points:.2f} pp")

    st.write("DEBUG result:", result)
    st.write("DEBUG result dict:", result.__dict__)
    st.metric("Standard error (σ₍δ₎)", f"{result.se:.4f}")
    st.metric("Degrees of freedom", f"{result.df}")
    
    st.metric("Design effect (DEFF)", f"{result.design_effect:.3f}")
    st.metric("Effective sample size", f"{result.effective_n:,.1f}")
    st.metric("Total sample size", f"{result.total_n}")

    interp = interpret_mdes(
        mdes=result.mdes,
        outcome_type=state.get("outcome_type", "continuous"),
        baseline_prob=state.get("baseline_prob"),
        alpha=state.get("alpha", 0.05),
        power=state.get("power", 0.80),
    )
    st.markdown("### Interpretation")
    st.write(interp["narrative"])
    
# ---------------------------------------------------------------------
# Top-level calculator assembly
# ---------------------------------------------------------------------

def render_calculator_page(design):
    with st.container():
        render_header(design)

    st.markdown("---")

    state = read_initial_state(design)

    with st.container():
        render_outcome_type_inputs(design, state)
        st.markdown("---")

    # 4. Sample size inputs
    with st.container():
        render_sample_inputs(design, state)

    # 5. ICC + covariates
    with st.container():
        render_icc_covariate_inputs(design, state)

    # 6. Blocking (if applicable)
    if design.calculator_config.get("block_fields"):
        with st.container():
            render_block_inputs(design, state)

    # 7. Cluster structure (if applicable)
    if design.calculator_config.get("cluster_fields"):
        with st.container():
            render_cluster_inputs(design, state)

    # 8. RD inputs (if applicable)
    if design.calculator_config.get("rd_fields"):
        with st.container():
            render_rd_inputs(design, state)

    # 9. ITS inputs (if applicable)
    if design.calculator_config.get("its_fields"):
        with st.container():
            render_its_inputs(design, state)

    # 10. Test settings
    with st.container():
        render_test_settings(design, state)
        st.markdown("---")

    # 11. Run engine + results
    if st.button("Compute MDES"):
        inputs = collect_engine_inputs(design, state)
        result = run_engine(design, inputs)
        render_results(result, state)
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

    # Test settings (always alpha + power + two_tailed)
    for field in ["alpha", "power", "two_tailed"]:
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
from mdes_engines.bira import compute_mdes_bira2_1c
from mdes_engines.bira import compute_mdes_bira2_1r
from mdes_engines.bira import compute_mdes_bira2_1f
from mdes_engines.bira import compute_mdes_bira3_1r
from mdes_engines.bira import compute_mdes_bira4_1r

from mdes_engines.cra import compute_mdes_cra
from mdes_engines.mdes_four_level import compute_mdes_cra4_4
from mdes_engines.mdes_three_level import compute_mdes_cra3_3

from mdes_engines.bcra import compute_mdes_bcra
from mdes_engines.bcra import compute_mdes_bcra3_2r
from mdes_engines.bcra import compute_mdes_bcra3_2f
from mdes_engines.mdes_four_level import compute_mdes_bcra4_3r
from mdes_engines.mdes_four_level import compute_mdes_bcra4_3f
from mdes_engines.mdes_four_level import compute_mdes_bcra4_2

from mdes_engines.rd import compute_mdes_rd

from mdes_engines.its import compute_mdes_its

ENGINE_MAP = {
    "compute_mdes_ira": compute_mdes_ira,
    "compute_mdes_bira": compute_mdes_bira,
    "compute_mdes_bira2_1c": compute_mdes_bira2_1c,
    "compute_mdes_bira2_1r": compute_mdes_bira2_1r,
    "compute_mdes_bira2_1f": compute_mdes_bira2_1f,
    "compute_mdes_bira3_1r": compute_mdes_bira3_1r,
    "compute_mdes_bira4_1r": compute_mdes_bira4_1r,
    "compute_mdes_cra": compute_mdes_cra,
    "compute_mdes_cra3_3": compute_mdes_cra3_3,
    "compute_mdes_cra4_4": compute_mdes_cra4_4,
    "compute_mdes_bcra": compute_mdes_bcra,
    "compute_mdes_bcra3_2r": compute_mdes_bcra3_2r,
    "compute_mdes_bcra3_2f": compute_mdes_bcra3_2f,
    "compute_mdes_bcra4_3r": compute_mdes_bcra4_3r,
    "compute_mdes_bcra4_3f": compute_mdes_bcra4_3f,
    "compute_mdes_bcra4_2": compute_mdes_bcra4_2,
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
        + cfg.get("two_tailed_field", [])
        + cfg.get("icc_fields", [])
        + cfg.get("covariate_fields", [])
        + cfg.get("block_fields", [])
        + cfg.get("cluster_fields", [])
        + cfg.get("rd_fields", [])
        + cfg.get("its_fields", [])
        + ["alpha", "power"]
    )

    # Collect inputs in design-specific order
    inputs_dict = {}
    for field in ordered_fields:
        if field in state:
            inputs_dict[field] = state[field]
    inputs_dict['outcome_type'] = state.get('outcome_type')
    if state.get('outcome_type') == 'binary':
        inputs_dict['baseline_prob'] = state.get('baseline_prob')
        inputs_dict['outcome_sd']    = state.get('outcome_sd')
    else:
        sd = state.get('outcome_sd_input')
        if sd is not None:
            inputs_dict['outcome_sd_input'] = sd
        inputs_dict['outcome_sd'] = state.get('outcome_sd')

    # Build narrative strings via interpret_mdes
    interp = interpret_mdes(
        mdes=result.mdes,
        outcome_type=state.get('outcome_type', 'continuous'),
        baseline_prob=state.get('baseline_prob'),
        alpha=state.get('alpha', 0.05),
        power=state.get('power', 0.80),
    )
    narrative      = interp.get('narrative', 'Not provided.')
    calc_narrative = (
        f"The MDES was computed using the {design_title} design, "
        f"which applies a {state.get('two_tailed', True) and 'two-tailed' or 'one-tailed'} test with "
        f"\u03b1={state.get('alpha', 0.05)} and "
        f"power={state.get('power', 0.80)}. Variance components and covariate "
        f"adjustments were incorporated according to the design\u2019s statistical "
        f"model. For continuous outcomes, effect-size interpretation follows "
        f"Kraft (2020)."
    )

    from services.export import generate_docx
    from datetime import datetime
    docx_buffer = generate_docx(
        title=design_title,
        inputs=inputs_dict,
        results=result,
        narrative=narrative,
        calc_narrative=calc_narrative,
        metadata={},
    )

    st.download_button(
        label='\U0001F4C4 Download Results (.docx)',
        data=docx_buffer,
        file_name=f"mdes_results_{datetime.now().strftime('%Y%m%d%H%M')}.docx",
        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
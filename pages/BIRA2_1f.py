import streamlit as st
from config.designs import DESIGN_BY_CODE
from calculator_ui import (
    read_initial_state,
    render_header,
    render_sample_inputs,
    render_icc_covariate_inputs,
    render_test_settings,
    render_outcome_type_inputs,
    collect_engine_inputs,
    run_engine,
    render_download_button,
)

DESIGN_CODE = __file__.split("/")[-1].replace(".py", "")
design = DESIGN_BY_CODE[DESIGN_CODE]

state = read_initial_state(design)

render_header(design)

sample = render_sample_inputs(design, state)
icc_cov = render_icc_covariate_inputs(design, state)
test = render_test_settings(state)
outcome = render_outcome_type_inputs(design, state)

inputs = collect_engine_inputs(design, sample, icc_cov, test, outcome)

if st.button("Compute MDES"):
    result = run_engine(design, inputs)
    st.subheader("Results")
    st.write(result)
    render_download_button(result, state, design.title)

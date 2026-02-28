# generate_pages.py

import os
from config.designs import DESIGNS

TEMPLATE = """import streamlit as st
import os
from config.designs import DESIGN_BY_CODE
from services.calculator_ui import (
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

DESIGN_CODE = os.path.splitext(os.path.basename(__file__))[0]
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

"""

def main():
    pages_dir = "pages"
    os.makedirs(pages_dir, exist_ok=True)

    for d in DESIGNS:
        filename = os.path.join(pages_dir, f"{d.code}.py")

        if os.path.exists(filename):
            print(f"Skipping existing file: {filename}")
            continue

        with open(filename, "w", encoding="utf-8") as f:
            f.write(TEMPLATE)

        print(f"Created: {filename}")

if __name__ == "__main__":
    main()
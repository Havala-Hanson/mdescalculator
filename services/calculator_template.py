import streamlit as st
from datetime import datetime
from services.interpretation import interpret_mdes
from services.export import generate_docx
from services.narrative import build_methodology
from services.report_customization import render_customize_report
from services.sensitivity import (
    render_sensitivity_controls,
    build_best_and_worst_inputs,
    render_sensitivity_panel,
    run_engine_safe,
)


def render_calculator_page(
    design,
    input_render_fn,
    engine_fn,
    sensitivity_fields=None,
):
    st.subheader(design.title)
    st.write(design.description)

    # -----------------------------
    # Inputs
    # -----------------------------
    with st.form("calculator_form"):
        inputs = input_render_fn(design)

        if sensitivity_fields:
            sens_enabled, sens_ranges = render_sensitivity_controls(
                inputs, sensitivity_fields
            )
        else:
            sens_enabled, sens_ranges = False, {}

        submitted = st.form_submit_button("Compute MDES")

    # -----------------------------
    # On submit: compute + cache in session state so later reruns
    # (e.g., typing in the outside-form Customize report inputs) don't
    # wipe the results.
    # -----------------------------
    cache_key = f"_calc_cache_{design.code}"

    if submitted:
        try:
            result = engine_fn(**inputs)
        except ValueError as e:
            st.error(str(e))
            st.session_state.pop(cache_key, None)
            return

        sensitivity_data = None
        if sens_enabled and sens_ranges:
            best_inputs, worst_inputs = build_best_and_worst_inputs(inputs, sens_ranges)
            sensitivity_data = {
                "best_inputs":  best_inputs,
                "best_result":  run_engine_safe(engine_fn, best_inputs),
                "worst_inputs": worst_inputs,
                "worst_result": run_engine_safe(engine_fn, worst_inputs),
            }

        st.session_state[cache_key] = {
            "result": result,
            "inputs": inputs,
            "sensitivity": sensitivity_data,
        }

    cached = st.session_state.get(cache_key)
    if cached is None:
        return

    result = cached["result"]
    inputs = cached["inputs"]
    sensitivity_data = cached["sensitivity"]
    outcome_type = inputs.get("outcome_type")

    interp = interpret_mdes(
        mdes=result.mdes,
        outcome_type=outcome_type,
        baseline_prob=inputs.get("baseline_prob"),
        alpha=inputs["alpha"],
        power=inputs["power"],
    )

    # -----------------------------
    # Results
    # -----------------------------
    st.subheader("Results")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("MDES (standardized)", f"{result.mdes:.4f}")
        if outcome_type == "binary" and result.mdes_pct_points is not None:
            st.metric("MDES (percentage points)", f"{result.mdes_pct_points:.2f} pp")
        elif result.mdes_standardized is not None:
            st.metric("MDES (raw units)", f"{result.mdes_standardized:.4f}")

    with col2:
        st.metric("Standard error", f"{result.se:.4f}")
        st.metric("Degrees of freedom", f"{result.df}")
        if result.design_effect is not None:
            st.metric("Design effect (DEFF)", f"{result.design_effect:.3f}")
        if result.effective_n is not None:
            st.metric("Effective N", f"{result.effective_n:.1f}")
        st.metric("Total N", f"{result.total_n}")

    # -----------------------------
    # Interpretation panel
    # -----------------------------
    st.subheader("Interpretation")

    if interp["label"] is not None:
        st.markdown(f"**Effect size classification:** {interp['label']}")

    if interp["new_percentile"] is not None:
        st.markdown(
            f"**Equivalent percentile shift:** moves a median individual "
            f"to the **{interp['new_percentile']:.1f}th percentile** "
            f"({interp['percentile_shift']:.1f} percentile‑point shift)"
        )

    if interp["relative_change"] is not None:
        st.markdown(
            f"**Relative change:** {interp['relative_change']:.1f}% increase "
            f"over the baseline rate"
        )

    st.write(interp["narrative"])

    # -----------------------------
    # Sensitivity analysis (render from cache)
    # -----------------------------
    if sensitivity_data:
        render_sensitivity_panel(
            best_result=sensitivity_data["best_result"],
            main_result=result,
            worst_result=sensitivity_data["worst_result"],
            outcome_type=outcome_type,
        )

    # -----------------------------
    # Customize report (label inputs for the .docx narrative)
    # -----------------------------
    labels_raw = render_customize_report(design)

    # -----------------------------
    # Export
    # -----------------------------
    st.subheader("Download report")

    methodology_blocks = build_methodology(
        design=design,
        inputs=inputs,
        result=result,
        outcome_type=outcome_type,
        labels_raw=labels_raw,
        sensitivity=sensitivity_data,
    )

    report_bytes = generate_docx(
        title=design.title,
        inputs=inputs,
        results=result,
        narrative=interp["narrative"],
        methodology_blocks=methodology_blocks,
        sensitivity=sensitivity_data,
    )

    st.download_button(
        label="\U0001F4C4 Download Results (.docx)",
        data=report_bytes,
        file_name=f"{design.code}_mdes_report_{datetime.now().strftime('%Y%m%d%H%M')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
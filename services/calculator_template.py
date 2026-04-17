import streamlit as st
from datetime import datetime
from services.interpretation import interpret_mdes
from services.export import generate_docx


def render_calculator_page(
    design,
    input_render_fn,
    engine_fn,
):
    st.subheader(design.title)
    st.write(design.description)

    # -----------------------------
    # Inputs
    # -----------------------------
    with st.form("calculator_form"):
        inputs = input_render_fn(design)
        submitted = st.form_submit_button("Compute MDES")

    if not submitted:
        return

    # -----------------------------
    # Compute
    # -----------------------------
    try:
        result = engine_fn(**inputs)
    except ValueError as e:
        st.error(str(e))
        return

    # -----------------------------
    # Interpretation
    # -----------------------------
    interp = interpret_mdes(
        mdes=result.mdes,
        outcome_type=inputs["outcome_type"],
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
        if result.mdes_pct_points is not None:
            st.metric("MDES (percentage points)", f"{result.mdes_pct_points:.2f}")

    with col2:
        st.metric("Standard error", f"{result.se:.4f}")
        st.metric("Degrees of freedom", f"{result.df}")
        st.metric("Effective N", f"{result.effective_n:.1f}")

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
    # Export
    # -----------------------------
    st.subheader("Download report")

    calc_narrative = (
        f"The MDES was computed using the {design.title} design, "
        f"which applies a two-tailed test with "
        f"\u03b1={inputs.get('alpha', 0.05)} and "
        f"power={inputs.get('power', 0.80)}. Variance components and covariate "
        f"adjustments were incorporated according to the design\u2019s statistical "
        f"model. For continuous outcomes, effect-size interpretation follows "
        f"Kraft (2020)."
    )

    report_bytes = generate_docx(
        title=design.title,
        inputs=inputs,
        results=result,
        narrative=interp["narrative"],
        calc_narrative=calc_narrative,
    )

    st.download_button(
        label="\U0001F4C4 Download Results (.docx)",
        data=report_bytes,
        file_name=f"{design.code}_mdes_report_{datetime.now().strftime('%Y%m%d%H%M')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
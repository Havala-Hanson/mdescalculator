import streamlit as st
import pandas as pd
from config.designs import DESIGN_BY_CODE

def render_comparison():
    left_code = st.session_state.get("compare_left")
    right_code = st.session_state.get("compare_right")

    if not left_code or not right_code:
        st.error("No designs selected for comparison.")
        return

    left = DESIGN_BY_CODE[left_code]
    right = DESIGN_BY_CODE[right_code]

    st.header(f"Comparing {left.title} and {right.title}")

    st.subheader("Conceptual difference")
    st.write(
        f"{left.title} is a {left.design_family} design, while "
        f"{right.title} is a {right.design_family} design. "
        "The table below highlights where these designs differ structurally."
    )

    # Build comparison table
    data = {
        "Feature": [
            "Assignment unit",
            "Levels",
            "Blocked",
            "Block effects",
            "Nesting",
            "Randomization / QED type",
        ],
        left.title: [
            left.assignment_unit,
            left.levels,
            left.is_blocked,
            left.block_effect or "—",
            left.nesting or "—",
            left.design_family,
        ],
        right.title: [
            right.assignment_unit,
            right.levels,
            right.is_blocked,
            right.block_effect or "—",
            right.nesting or "—",
            right.design_family,
        ],
    }

    df = pd.DataFrame(data)
    df["__diff__"] = df[left.title] != df[right.title]

    st.subheader("Structural comparison")
    show_differences_only = st.checkbox("Show differences only", value=False)

    if show_differences_only:
        df_display = df[df["__diff__"]].copy()
        if df_display.empty:
            st.info("These two designs are structurally identical based on the available metadata.")
            df_display = df.copy()
    else:
        df_display = df.copy()

    def highlight_differences(row):
        if row["__diff__"]:
            return ["background-color: #fff3cd"] * (len(row) - 1) + [""]
        return [""] * len(row)

    df_display = df_display.drop(columns=["__diff__"])
    st.dataframe(df_display.style.apply(highlight_differences, axis=1), use_container_width=True)

    # Contextual explanations for differing features
    EXPLANATIONS = {
        "Assignment unit": (
            "The assignment unit determines which variance components drive power. "
            "Cluster-level assignment introduces between-cluster variance that must be modeled explicitly."
        ),
        "Levels": (
            "Higher-level designs require modeling additional variance components, which affects power and required sample sizes."
        ),
        "Blocked": (
            "Blocked designs can improve precision by controlling for block-level differences, "
            "but require specifying a blocking variable."
        ),
        "Block effects": (
            "Block effects determine whether blocks are treated as fixed, random, or constant, which changes the model structure."
        ),
        "Nesting": (
            "Nesting introduces hierarchical structure that requires additional random effects in the model."
        ),
        "Randomization / QED type": (
            "Randomized designs rely on random assignment, while quasi-experimental designs rely on identifying assumptions "
            "such as cutoffs or time trends."
        ),
    }

    st.subheader("What the differences mean")
    for _, row in df.iterrows():
        if row["__diff__"]:
            feature = row["Feature"]
            explanation = EXPLANATIONS.get(feature)
            if explanation:
                st.write(f"- **{feature}** — {explanation}")

    # Calculator-specific implications
    st.subheader("Calculator-specific implications")

    def calculator_implications(design):
        notes = []

        # Assignment unit
        if design.assignment_unit == "individual":
            notes.append("Power depends primarily on individual-level variance; cluster ICCs are not required.")
        else:
            notes.append("Power depends on between-cluster variance; cluster ICCs and cluster sample sizes are required.")

        # Levels
        if design.levels == 2:
            notes.append("Requires specifying a two-level ICC and cluster sample sizes.")
        elif design.levels == 3:
            notes.append("Requires specifying classroom- and school-level ICCs and sample sizes at each level.")

        # Blocking
        if design.is_blocked:
            notes.append("Requires specifying the number of blocks and block effects, which influence precision.")

        # Block effects
        if design.block_effect == "random":
            notes.append("Requires estimating a block-level variance component.")
        elif design.block_effect == "fixed":
            notes.append("Requires specifying block indicators but does not add variance components.")

        # QED families
        if design.design_family == "RD":
            notes.append("Requires specifying the running variable distribution, bandwidth, and functional form.")
        elif design.design_family == "ITS":
            notes.append("Requires specifying pre/post time points, autocorrelation, and trend parameters.")

        # MDES engine mapping
        if design.levels == 2 and not design.is_blocked:
            notes.append("Uses the two-level MDES engine.")
        elif design.levels == 3:
            notes.append("Uses the three-level MDES engine.")
        elif design.is_blocked:
            notes.append("Uses the blocked MDES engine.")
        
        from services.prepopulate import prepopulate_for_design

        st.write(f"### {left.title}")
        for note in calculator_implications(left):
            st.write(f"- {note}")

        if st.button(f"Send {left.title} to calculator", key="calc_left"):
            prepopulate_for_design(left.code, st.session_state, outcome_type)
            st.switch_page(left.page)


        st.write(f"### {right.title}")
        for note in calculator_implications(right):
            st.write(f"- {note}")

        if st.button(f"Send {right.title} to calculator", key="calc_right"):
            prepopulate_for_design(right.code, st.session_state, outcome_type)
            st.switch_page(right.page)

        return notes


    st.subheader("How the classifier interpreted your description")
    st.write(
        "The classifier selected the primary design based on the strongest signals in your prompt. "
        "If the alternative design appears close in the comparison panel, it may be because your "
        "description contained partial cues for both designs or lacked details that would clearly "
        "distinguish between them."
    )

    render_comparison()
import streamlit as st
from services.classifier import classify_study
from config.designs import DESIGN_BY_CODE


# ---------------------------------------------------------------------
# Helper: pick a representative design for a family
# ---------------------------------------------------------------------
def representative_design_for_family(family: str):
    candidates = [d for d in DESIGN_BY_CODE.values() if d.design_family == family]
    if not candidates:
        return None
    candidates = sorted(candidates, key=lambda d: (d.is_blocked, d.levels))
    return candidates[0]


# ---------------------------------------------------------------------
# Main rendering function
# ---------------------------------------------------------------------
def render_classifier_results(user_text: str):
    result = classify_study(user_text)
    design_info = DESIGN_BY_CODE.get(result.design)

    # Guard against unknown design codes
    if design_info is None:
        st.error(f"Unknown design code returned: {result.design}")
        st.stop()

    st.header("Suggested Study Design")

    # -----------------------------------------------------------------
    # Design summary
    # -----------------------------------------------------------------
    st.subheader(f"{design_info.title} ({design_info.code})")
    st.write(design_info.description)

    # -----------------------------------------------------------------
    # Confidence visualization
    # -----------------------------------------------------------------
    st.markdown("### Confidence")
    st.progress(result.confidence)
    st.caption(
        f"Confidence score: **{result.confidence:.2f}** — "
        + (
            "high confidence" if result.confidence >= 0.75 else
            "moderate confidence" if result.confidence >= 0.45 else
            "low confidence"
        )
    )

    # -----------------------------------------------------------------
    # Optional hint
    # -----------------------------------------------------------------
    with st.expander("How to read this panel"):
        st.write(
            "This summary breaks your description into four parts: "
            "what evidence supported the chosen design, why other designs were ruled out, "
            "what details were unclear, and how you could strengthen the description next time. "
            "These sections help you understand how the classifier interpreted your prompt."
        )

    # -----------------------------------------------------------------
    # Parse rationale into structured sections (more resilient)
    # -----------------------------------------------------------------
    rationale = result.rationale or ""
    sentences = [
        s.strip()
        for s in rationale.replace("\n", " ").split(".")
        if s.strip()
    ]

    evidence_for = []
    evidence_against = []
    missing_info = []
    improvement = []

    for s in sentences:
        s_lower = s.lower()

        if s_lower.startswith("suggested because"):
            evidence_for.append(s[len("Suggested because"):].strip())

        elif s_lower.startswith("other designs were ruled out because"):
            evidence_against.append(
                s[len("Other designs were ruled out because"):].strip()
            )

        elif s_lower.startswith("some details were unclear"):
            # Extract after "including" if present
            if "including" in s_lower:
                missing_info.append(s.split("including", 1)[-1].strip())
            else:
                missing_info.append(s.strip())

        elif s_lower.startswith("to improve classification"):
            improvement.append(
                s[len("To improve classification,"):].strip()
            )

    # -----------------------------------------------------------------
    # Evidence supporting the chosen design
    # -----------------------------------------------------------------
    if evidence_for:
        st.markdown("### Why this design fits your description")
        for e in evidence_for:
            st.write(f"- {e}")

    # -----------------------------------------------------------------
    # Why other designs were ruled out
    # -----------------------------------------------------------------
    if evidence_against:
        st.markdown("### Why other designs were not selected")
        for e in evidence_against:
            st.write(f"- {e}")

    # -----------------------------------------------------------------
    # Missing or ambiguous information
    # -----------------------------------------------------------------
    if missing_info:
        st.markdown("### Details that were unclear or ambiguous")
        for m in missing_info:
            st.write(f"- {m}")

    # -----------------------------------------------------------------
    # How to improve the prompt
    # -----------------------------------------------------------------
    if improvement:
        st.markdown("### How to strengthen your description next time")
        for g in improvement:
            st.write(f"- {g}")

    # -----------------------------------------------------------------
    # Similar designs and how they differ
    # -----------------------------------------------------------------
    st.markdown("### Similar designs and how they differ")

    sorted_families = sorted(
        result.family_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    chosen_family = design_info.design_family

    FAMILY_DESCRIPTIONS = {
        "IRA": "individual-level randomization",
        "BIRA": "individual-level randomization within blocks",
        "CRA": "cluster-level randomization",
        "BCRA": "cluster-level randomization within blocks",
        "RD": "cutoff-based assignment (regression discontinuity)",
        "ITS": "longitudinal before/after structure (interrupted time series)",
    }

    for fam, score in sorted_families[:3]:
        rep = representative_design_for_family(fam)

        if fam == chosen_family:
            st.write(f"**{fam}** — selected (score {score:.2f})")
            st.caption(FAMILY_DESCRIPTIONS.get(fam, ""))
        else:
            st.write(f"**{fam}** — alternative (score {score:.2f})")
            st.caption(f"Conceptually: {FAMILY_DESCRIPTIONS.get(fam, '')}")

            # Why it wasn't selected
            if fam in ("RD", "ITS") and chosen_family not in ("RD", "ITS"):
                st.caption(
                    "Not selected because the prompt did not include cutoff or time-series structure."
                )
            elif fam in ("IRA", "BIRA") and chosen_family not in ("IRA", "BIRA"):
                st.caption(
                    "Not selected because individual-level assignment signals were weaker than cluster-level signals."
                )
            elif fam in ("CRA", "BCRA") and chosen_family not in ("CRA", "BCRA"):
                st.caption(
                    "Not selected because cluster-level signals were weaker than individual-level or quasi-experimental signals."
                )
            elif fam.startswith("B") and not design_info.is_blocked:
                st.caption(
                    "Not selected because blocking language was weak or ambiguous."
                )
            else:
                st.caption(
                    "Not selected because the overall pattern of evidence favored the chosen design."
                )

            # Comparison link
            if rep:
                if st.button(f"Compare with {rep.title}", key=f"compare_{fam}"):
                    st.session_state.compare_left = result.design
                    st.session_state.compare_right = rep.code
                    st.switch_page("pages/compare_designs.py")

    # -----------------------------------------------------------------
    # Navigation to calculator
    # -----------------------------------------------------------------
    if st.button("Open calculator for this design"):
        st.switch_page(design_info.page)

    # -----------------------------------------------------------------
    # Refinement panel
    # -----------------------------------------------------------------
    st.markdown("---")
    st.subheader("Refine your description")

    refined_text = st.text_area(
        "Adjust or expand your study description",
        value=user_text,
        height=100,
        key="refine_text_input"
    )

    if st.button("Re-run classification", key="refine_button"):
        if not refined_text.strip():
            st.warning("Please enter a study description.")
        else:
            st.session_state["classifier_input"] = refined_text
            st.rerun()


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if "classifier_input" not in st.session_state:
    st.error("No study description found. Please return to the homepage.")
    st.stop()

user_text = st.session_state["classifier_input"]
render_classifier_results(user_text)
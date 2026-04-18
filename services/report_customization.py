"""
'Customize report' section — renders text_input fields for each label slot the
design uses, so users can tailor the .docx narrative. Blank fields fall back to
defaults declared in `config/narrative_specs.py`.
"""

import streamlit as st

from config.narrative_specs import NARRATIVE_SPECS


SLOT_PROMPTS = {
    "level1":         "Level-1 unit (plural)",
    "level2":         "Level-2 unit (plural)",
    "level3":         "Level-3 unit (plural)",
    "level4":         "Level-4 unit (plural)",
    "timepoint_pre":  "Pre-intervention time point label (plural)",
    "timepoint_post": "Post-intervention time point label (plural)",
}


def render_customize_report(design):
    """Render the Customize report section and return a labels dict suitable
    for `narrative.build_methodology(labels_raw=...)`."""
    st.subheader("Customize report")
    st.caption("Optionally, specify details for the report.")

    spec = NARRATIVE_SPECS.get(design.code)
    if spec is None:
        return {}

    raw = {}
    defaults = spec.get("default_labels", {})
    for slot, default in defaults.items():
        prompt = SLOT_PROMPTS.get(slot, slot)
        raw[slot] = st.text_input(
            prompt,
            value="",
            placeholder=default,
            key=f"label_{design.code}_{slot}",
        )
    return raw

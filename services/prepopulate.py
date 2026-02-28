from config.defaults import DEFAULT_INPUTS
from config.designs import DESIGN_BY_CODE

def prepopulate_for_design(design_code, session_state, outcome_type="continuous"):
    design = DESIGN_BY_CODE[design_code]
    family = design.design_family

    family_defaults = DEFAULT_INPUTS.get(family, {})

    # Load shared defaults
    for key, value in family_defaults.get("shared", {}).items():
        session_state[key] = value

    # Load outcome-type-specific defaults
    outcome_defaults = family_defaults.get(outcome_type, {})
    for key, value in outcome_defaults.items():
        session_state[key] = value

    # Always store the selected design
    session_state["selected_design"] = design_code
    session_state["outcome_type"] = outcome_type
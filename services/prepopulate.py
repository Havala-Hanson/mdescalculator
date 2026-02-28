from config.defaults import DEFAULT_INPUTS

def prepopulate_for_design(design, session_state, outcome_type="continuous"):
    design_code = design.code
    family = design.design_family
    config = design.calculator_config  # design-specific field lists

    # Clear irrelevant keys
    for key in list(session_state.keys()):
        if key not in allowed_fields and key not in ["selected_design", "outcome_type"]:
            del session_state[key]

    # Collect all fields this design actually uses
    allowed_fields = (
        config.get("sample_fields", [])
        + config.get("icc_fields", [])
        + config.get("covariate_fields", [])
        + config.get("block_fields", [])
        + config.get("cluster_fields", [])
        + config.get("rd_fields", [])
        + config.get("its_fields", [])
        + ["alpha", "power"]  # always needed
    )

    family_defaults = DEFAULT_INPUTS.get(family, {})

    # Load shared defaults
    for key, value in family_defaults.get("shared", {}).items():
        if key in allowed_fields:
            session_state[key] = value

    # Load outcome-type-specific defaults
    outcome_defaults = family_defaults.get(outcome_type, {})
    for key, value in outcome_defaults.items():
        if key in allowed_fields:
            session_state[key] = value

    # Always store the selected design + outcome type
    session_state["selected_design"] = design_code
    session_state["outcome_type"] = outcome_type
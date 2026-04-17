from config.defaults import DEFAULT_INPUTS

def prepopulate_for_design(design, session_state, outcome_type="continuous"):
    design_code = design.code
    family = design.design_family
    config = design.calculator_config

    # ------------------------------------------------------------
    # 1. Determine allowed fields for this design
    # ------------------------------------------------------------
    allowed_fields = (
        config.get("sample_fields", [])
        + config.get("icc_fields", [])
        + config.get("covariate_fields", [])
        + config.get("block_fields", [])
        + config.get("cluster_fields", [])
        + config.get("rd_fields", [])
        + config.get("its_fields", [])
        + ["alpha", "power", "two_tailed"]
    )

    # ------------------------------------------------------------
    # 2. Only clear irrelevant keys when the design actually changes
    # ------------------------------------------------------------
    previous_design = session_state.get("selected_design")

    if previous_design != design_code:
        # Design changed → safe to clear irrelevant keys
        for key in list(session_state.keys()):
            if key not in allowed_fields and key not in ["selected_design", "outcome_type"]:
                del session_state[key]

    # ------------------------------------------------------------
    # 3. Apply defaults only when missing
    # ------------------------------------------------------------
    family_defaults = DEFAULT_INPUTS.get(family, {})

    # Shared defaults
    for key, value in family_defaults.get("shared", {}).items():
        if key in allowed_fields and key not in session_state:
            session_state[key] = value

    # Outcome-type defaults
    outcome_defaults = family_defaults.get(outcome_type, {})
    for key, value in outcome_defaults.items():
        if key in allowed_fields and key not in session_state:
            session_state[key] = value

    # ------------------------------------------------------------
    # 4. Store design + outcome type
    # ------------------------------------------------------------
    session_state["selected_design"] = design_code
    session_state["outcome_type"] = outcome_type
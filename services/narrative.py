"""
Build the Methodology & Calculations section of the .docx report as a list of
(subheading, body) tuples, one per block defined in
`agents/agent_docx_export.txt`.
"""

from config.narrative_specs import NARRATIVE_SPECS


# ----------------------------------------------------------------------
# Labels
# ----------------------------------------------------------------------

def _pluralize(word):
    """Simple rule-based plural. User can edit the .docx if the heuristic
    misses an irregular form."""
    if not word:
        return word
    low = word.lower()
    if low.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if low.endswith("y") and len(word) >= 2 and word[-2].lower() not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _singularize(word):
    """Naive singularizer — strip a trailing 's'/'es'. Used when we need
    'per {singular}' from a plural label."""
    if not word:
        return word
    low = word.lower()
    if low.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if low.endswith("es") and len(word) > 2 and low[-3] in "sxz" or low.endswith(("ches", "shes")):
        return word[:-2]
    if low.endswith("s") and not low.endswith("ss"):
        return word[:-1]
    return word


def build_label_dict(raw_labels, spec):
    """Fill in defaults for any blank slot the design needs, then derive
    singular and plural forms for every slot. Detects whether the input is
    already plural so 'student' and 'students' both work.

    raw_labels: {"level1": "student", ...} — may be partial or empty.
    spec: narrative spec for this design.
    """
    defaults = spec.get("default_labels", {})
    labels = {}
    for slot, default in defaults.items():
        entered = (raw_labels or {}).get(slot, "").strip()
        base = entered if entered else default
        low = base.lower()
        looks_plural = low.endswith("s") and not low.endswith("ss")
        if looks_plural:
            labels[f"{slot}_plural"]   = base
            labels[f"{slot}_singular"] = _singularize(base)
        else:
            labels[f"{slot}_singular"] = base
            labels[f"{slot}_plural"]   = _pluralize(base)
    return labels


# ----------------------------------------------------------------------
# Block builders — multilevel designs
# ----------------------------------------------------------------------

def _format_effects_list(slot_keys, labels, kind):
    """Turn ['level3_plural','level2_plural'] into 'schools and classrooms'."""
    if not slot_keys:
        return None
    items = [labels.get(k, k) for k in slot_keys]
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def model_definition_block(spec, labels):
    nesting = spec["nesting_text"].format(**labels)
    assignment = spec["assignment_text"].format(**labels)

    re_text = _format_effects_list(spec["random_effects"], labels, "random")
    fe_text = _format_effects_list(spec["fixed_effects"], labels, "fixed")

    if re_text and fe_text:
        effects_clause = (
            f"The statistical model includes random effects for {re_text} "
            f"and fixed effects for {fe_text}."
        )
    elif re_text:
        effects_clause = (
            f"The statistical model includes random effects for {re_text}."
        )
    elif fe_text:
        effects_clause = (
            f"The statistical model includes fixed effects for {fe_text}, "
            f"with no higher-level random effects."
        )
    else:
        effects_clause = (
            "The statistical model includes no higher-level random or fixed effects."
        )

    return (
        f"The analysis uses a {spec['design_label']}, in which {nesting}. "
        f"Treatment is assigned at {assignment}. {effects_clause} "
        f"All variance components and covariate adjustments are incorporated "
        f"according to this multilevel structure."
    )


def _format_param(param, inputs, labels):
    value = inputs.get(param["key"])
    slot_plural = labels.get(f"{param['unit_slot']}_plural", param["unit_slot"])
    per_slot = param.get("per_slot")
    if per_slot:
        per_singular = labels.get(f"{per_slot}_singular", per_slot)
        return f"{param['symbol']} = {value} {slot_plural} per {per_singular}"
    return f"{param['symbol']} = {value} {slot_plural}"


def sample_structure_block(spec, inputs, labels):
    parts = [_format_param(p, inputs, labels) for p in spec["params"]]
    if len(parts) == 1:
        formatted = parts[0]
    else:
        formatted = ", ".join(parts[:-1]) + f", and {parts[-1]}"
    return (
        f"The detectable effect size depends on the number of analytic units at each level. "
        f"Under the specified inputs, the design includes {formatted}. "
        f"These values determine the number of units contributing to each variance component "
        f"in the multilevel model."
    )


def statistical_assumptions_block(spec, inputs):
    p_key = spec.get("p_key")
    p_value = inputs.get(p_key, 0.5) if p_key else 0.5
    core = (
        f"The MDES calculation incorporates the specified assumptions about intraclass "
        f"correlations (ICCs) at each level, covariate R² values, and the proportion of "
        f"units assigned to treatment (p = {p_value}). These assumptions determine the "
        f"proportion of variance attributable to each level and the extent to which "
        f"covariates reduce residual variance."
    )

    if spec.get("uses_omega"):
        omega_sym = spec.get("omega_symbol", "ω")
        # engines name the param omega3/omega4/omega2 — try in priority order
        omega_value = (
            inputs.get("omega4")
            or inputs.get("omega3")
            or inputs.get("omega2")
            or 1.0
        )
        core += (
            f" A block-level treatment-effect heterogeneity parameter "
            f"({omega_sym} = {omega_value}) is additionally included, which inflates the "
            f"variance of the treatment effect across higher-level units."
        )
    return core


def outcome_block(outcome_type, inputs):
    if outcome_type == "binary":
        baseline = inputs.get("baseline_prob")
        baseline_clause = (
            f" p₀ = {baseline}" if baseline is not None else ""
        )
        return (
            f"The MDES is expressed in percentage-point units. Binary outcomes are modeled "
            f"using a Bernoulli variance structure, where the standard deviation is "
            f"computed as √(p₀(1−p₀)) based on the specified baseline probability{baseline_clause}. "
            f"The MDES therefore represents the minimum detectable difference in event "
            f"probability between treatment and control groups."
        )
    return (
        "The MDES is expressed in standardized effect-size units. Interpretation follows "
        "Kraft (2020), which contextualizes standardized effects using empirical benchmarks "
        "and percentile-shift transformations based on the normal distribution."
    )


def _param_string(inputs, spec, labels):
    return ", ".join(_format_param(p, inputs, labels) for p in spec["params"])


def _format_mdes(result, outcome_type):
    if isinstance(result, str):
        return f"(not computable: {result})"
    if outcome_type == "binary" and getattr(result, "mdes_pct_points", None) is not None:
        return f"{result.mdes_pct_points:.2f} pp"
    return f"{result.mdes:.4f}"


def sensitivity_block(spec, labels, outcome_type, main_inputs, main_result, sensitivity):
    if not sensitivity:
        return (
            "Because MDES values are sensitive to assumptions about ICCs, covariate R² "
            "values, and sample sizes at each level, results should be interpreted alongside "
            "sensitivity analyses that vary these parameters within plausible ranges."
        )

    best_inputs  = sensitivity["best_inputs"]
    worst_inputs = sensitivity["worst_inputs"]
    best_result  = sensitivity["best_result"]
    worst_result = sensitivity["worst_result"]

    main_mdes  = _format_mdes(main_result, outcome_type)
    best_mdes  = _format_mdes(best_result, outcome_type)
    worst_mdes = _format_mdes(worst_result, outcome_type)

    main_param_str  = _param_string(main_inputs,  spec, labels)
    best_param_str  = _param_string(best_inputs,  spec, labels)
    worst_param_str = _param_string(worst_inputs, spec, labels)

    return (
        f"A sensitivity analysis was conducted to assess how the MDES responds to plausible "
        f"variation in key design parameters. Minimum and maximum values were specified for "
        f"selected inputs, and for each parameter the direction that increases or decreases "
        f"MDES was used to assemble a best-case (smallest MDES) bundle and a worst-case "
        f"(largest MDES) bundle. "
        f"Under the primary specification ({main_param_str}), the MDES is {main_mdes}. "
        f"Under the most favorable assumptions for statistical precision ({best_param_str}), "
        f"the MDES is {best_mdes}. Under the least favorable assumptions ({worst_param_str}), "
        f"the MDES is {worst_mdes}. This range quantifies the robustness of the design to "
        f"uncertainty in the specified inputs."
    )


def reproducibility_block():
    return (
        "All calculations were performed using the Precision MDES engine, a validated "
        "analytic core aligned with the PowerUpR implementation (Dong & Maynard, 2013), "
        "ensuring reproducibility of inputs, assumptions, and intermediate quantities."
    )


# ----------------------------------------------------------------------
# ITS (time-series) — custom block builders
# ----------------------------------------------------------------------

def _its_model_definition(spec, inputs, labels):
    return (
        "The analysis uses an interrupted time series design, in which a single outcome "
        "is observed repeatedly before and after an intervention point. The statistical "
        "model estimates a level shift at the intervention, adjusting for pre-intervention "
        "trend and serial autocorrelation. Treatment is not randomized; identification "
        "relies on the assumption of a stable counterfactual trajectory in the absence of "
        "the intervention."
    )


def _its_sample_structure(spec, inputs, labels):
    pre = inputs.get("n_timepoints_pre")
    post = inputs.get("n_timepoints_post")
    return (
        f"Under the specified inputs, the design includes {pre} pre-intervention time "
        f"points and {post} post-intervention time points contributing to the estimation "
        f"of the level shift."
    )


def _its_statistical_assumptions(spec, inputs):
    rho = inputs.get("autocorrelation")
    rho_clause = f" (ρ = {rho})" if rho is not None else ""
    return (
        f"The MDES calculation incorporates the specified first-order autocorrelation "
        f"between adjacent time points{rho_clause}, which determines the effective number "
        f"of independent observations and therefore the precision of the estimated shift."
    )


# ----------------------------------------------------------------------
# Top-level assembler
# ----------------------------------------------------------------------

def build_methodology(design, inputs, result, outcome_type,
                      labels_raw=None, sensitivity=None):
    """
    Return a list of (subheading, body) tuples ready for the .docx's
    Methodology & Calculations section.
    """
    spec = NARRATIVE_SPECS.get(design.code)
    if spec is None:
        # graceful fallback: one generic paragraph
        return [(
            "Overview",
            f"The MDES was computed using the {design.title} design."
        )]

    kind = spec.get("kind", "multilevel")
    labels = build_label_dict(labels_raw, spec)

    if kind == "time_series":
        blocks = [
            ("Model Definition",        _its_model_definition(spec, inputs, labels)),
            ("Sample Structure",        _its_sample_structure(spec, inputs, labels)),
            ("Statistical Assumptions", _its_statistical_assumptions(spec, inputs)),
        ]
    else:
        blocks = [
            ("Model Definition",        model_definition_block(spec, labels)),
            ("Sample Structure",        sample_structure_block(spec, inputs, labels)),
            ("Statistical Assumptions", statistical_assumptions_block(spec, inputs)),
        ]

    blocks += [
        ("Outcome Type", outcome_block(outcome_type, inputs)),
        ("Sensitivity Analysis",
         sensitivity_block(spec, labels, outcome_type, inputs, result, sensitivity)),
        ("Reproducibility", reproducibility_block()),
    ]
    return blocks

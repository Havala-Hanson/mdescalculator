import streamlit as st
from copy import deepcopy


# --------------------------------------------------------------------
# Field metadata
# --------------------------------------------------------------------
# Widget labels. Each entry is (kind, noun). kind controls phrasing:
#   "count" -> "Minimum number of {noun}"
#   "value" -> "Minimum value of {noun}"
FIELD_LABELS = {
    # Sample sizes
    "n_individuals":        ("count", "individuals"),
    "n_blocks":             ("count", "blocks"),
    "n_clusters":           ("count", "clusters"),
    "n_clusters_per_block": ("count", "clusters per block"),
    "n_sites_per_block":    ("count", "sites per block"),
    "n_clusters_per_site":  ("count", "clusters per site"),
    "n_level2":             ("count", "level-2 units"),
    "n_level3":             ("count", "level-3 units"),
    "n_level4":             ("count", "level-4 units (blocks)"),
    "cluster_size":         ("count", "units per cluster"),
    "n_timepoints_pre":     ("count", "pre-intervention time points"),
    "n_timepoints_post":    ("count", "post-intervention time points"),
    # ICCs
    "icc":                  ("value", "ICC"),
    "icc2":                 ("value", "ICC at level 2"),
    "icc3":                 ("value", "ICC at level 3"),
    "icc4":                 ("value", "ICC at level 4"),
    # R²
    "r2_level1":            ("value", "R² (level-1 covariates)"),
    "r2_level2":            ("value", "R² (level-2 covariates)"),
    "r2_level3":            ("value", "R² (level-3 covariates)"),
    "r2_level4":            ("value", "R² (level-4 covariates)"),
    "r2_treat3":            ("value", "R² (level-3 treatment-variance covariates)"),
    "r2_treat4":            ("value", "R² (level-4 treatment-variance covariates)"),
    # ω (treatment heterogeneity)
    "omega2":               ("value", "ω₂ (level-2 treatment heterogeneity)"),
    "omega3":               ("value", "ω₃ (level-3 treatment heterogeneity)"),
    "omega4":               ("value", "ω₄ (level-4 treatment heterogeneity)"),
    # Treatment allocation (proportion in [0, 1])
    "p":                    ("value", "treatment allocation (p)"),
    "p_treat":              ("value", "treatment allocation ratio (p)"),
    "prop_treated":         ("value", "proportion treated"),
    # Covariate counts for df adjustment
    "g1":                   ("count", "level-1 covariates"),
    "g2":                   ("count", "level-2 covariates"),
    "g3":                   ("count", "level-3 covariates"),
    "g4":                   ("count", "level-4 covariates"),
    # ITS
    "autocorrelation":      ("value", "autocorrelation (ρ)"),
}


# Direction relative to MDES:
#   "inverse" -> field ↑ ⇒ MDES ↓  (sample sizes, R² covariates)
#   "direct"  -> field ↑ ⇒ MDES ↑  (ICCs, ω, autocorrelation)
MDES_DIRECTION = {
    "n_individuals":        "inverse",
    "n_blocks":             "inverse",
    "n_clusters":           "inverse",
    "n_clusters_per_block": "inverse",
    "n_sites_per_block":    "inverse",
    "n_clusters_per_site":  "inverse",
    "n_level2":             "inverse",
    "n_level3":             "inverse",
    "n_level4":             "inverse",
    "cluster_size":         "inverse",
    "n_timepoints_pre":     "inverse",
    "n_timepoints_post":    "inverse",
    "r2_level1":            "inverse",
    "r2_level2":            "inverse",
    "r2_level3":            "inverse",
    "r2_level4":            "inverse",
    "r2_treat3":            "inverse",
    "r2_treat4":            "inverse",
    "icc":                  "direct",
    "icc2":                 "direct",
    "icc3":                 "direct",
    "icc4":                 "direct",
    "omega2":               "direct",
    "omega3":               "direct",
    "omega4":               "direct",
    "autocorrelation":      "direct",
    # Treatment allocation: MDES is minimized at p=0.5 and U-shapes outward, so
    # the "direct" mapping is an approximation — the worst case is whichever
    # boundary is farther from 0.5. Tagged "direct" so the widget still works;
    # users vary both sides and inspect both bundles.
    "p":                    "direct",
    "p_treat":              "direct",
    "prop_treated":         "direct",
    # Covariate counts: more covariates → fewer degrees of freedom → larger MDES
    "g1":                   "direct",
    "g2":                   "direct",
    "g3":                   "direct",
    "g4":                   "direct",
}


# Category sets for per-type defaults
_ICC_FIELDS = {"icc", "icc2", "icc3", "icc4"}
_R2_FIELDS = {"r2_level1", "r2_level2", "r2_level3", "r2_level4",
              "r2_treat3", "r2_treat4"}
_OMEGA_FIELDS = {"omega2", "omega3", "omega4"}
_AUTOCORR_FIELDS = {"autocorrelation"}
_P_FIELDS = {"p", "p_treat", "prop_treated"}
_G_FIELDS = {"g1", "g2", "g3", "g4"}


def _label(field, bound):
    kind, noun = FIELD_LABELS.get(field, ("value", field))
    if kind == "count":
        return f"{bound} number of {noun}"
    return f"{bound} value of {noun}"


def _default_range(field, main_value):
    """Return (lo_default, hi_default, abs_min, abs_max, step, is_int)."""
    if field in _ICC_FIELDS:
        return (max(0.0, main_value - 0.03), min(0.99, main_value + 0.03),
                0.0, 0.99, 0.01, False)
    if field in _R2_FIELDS:
        return (max(0.0, main_value - 0.10), min(0.99, main_value + 0.10),
                0.0, 0.99, 0.05, False)
    if field in _OMEGA_FIELDS:
        return (max(0.0, main_value * 0.5), main_value * 1.5,
                0.0, None, 0.1, False)
    if field in _AUTOCORR_FIELDS:
        return (max(0.0, main_value - 0.10), min(0.99, main_value + 0.10),
                0.0, 0.99, 0.05, False)
    if field in _P_FIELDS:
        return (max(0.01, main_value - 0.10), min(0.99, main_value + 0.10),
                0.01, 0.99, 0.05, False)
    if field in _G_FIELDS:
        lo = max(0, int(main_value) - 2)
        hi = max(lo + 1, int(main_value) + 2)
        return (lo, hi, 0, None, 1, True)
    # Fallback: infer type from main_value so floats don't get int-typed widgets
    is_int = isinstance(main_value, int) and not isinstance(main_value, bool)
    if is_int:
        lo = max(1, int(round(main_value * 0.75)))
        hi = max(lo + 1, int(round(main_value * 1.25)))
        return (lo, hi, 1, None, 1, True)
    # Unknown float field — wide range, no absolute max
    lo = max(0.0, main_value * 0.5)
    hi = max(lo + 0.01, main_value * 1.5)
    return (lo, hi, 0.0, None, 0.01, False)


# --------------------------------------------------------------------
# UI
# --------------------------------------------------------------------

def render_sensitivity_controls(inputs, sensitivity_fields):
    """
    Render an expander containing a checkbox plus min/max inputs for each
    sensitivity field. Intended to be called inside a `st.form(...)` block
    so everything submits together.

    Returns (enabled, ranges) where ranges = {field: (lo, hi)}.
    """
    enabled = False
    ranges = {}

    with st.expander("Sensitivity analysis (optional)", expanded=False):
        enabled = st.checkbox(
            "Run sensitivity analysis",
            value=False,
            key="sens_enabled",
            help=(
                "Compute a best-case (smallest MDES) and worst-case (largest MDES) "
                "scenario alongside the main result. For each parameter, the bundle "
                "direction is chosen automatically based on whether that parameter "
                "increases or decreases MDES."
            ),
        )
        st.caption(
            "Min values must be ≤ the main value; max values must be ≥ the main value. "
            "Each parameter's min and max are assembled into the best/worst scenarios "
            "according to its effect on MDES."
        )

        for field in sensitivity_fields:
            main_value = inputs.get(field)
            if main_value is None:
                continue

            lo_default, hi_default, abs_min, abs_max, step, is_int = \
                _default_range(field, main_value)

            if is_int:
                lo_default = int(lo_default)
                hi_default = int(hi_default)

            lo_kwargs = {
                "min_value": abs_min,
                "max_value": main_value,
                "value": min(lo_default, main_value),
                "step": step,
                "key": f"sens_{field}_lo",
            }
            hi_kwargs = {
                "min_value": main_value,
                "value": max(hi_default, main_value),
                "step": step,
                "key": f"sens_{field}_hi",
            }
            if abs_max is not None:
                hi_kwargs["max_value"] = abs_max

            col_lo, col_hi = st.columns(2)
            with col_lo:
                lo = st.number_input(_label(field, "Minimum"), **lo_kwargs)
            with col_hi:
                hi = st.number_input(_label(field, "Maximum"), **hi_kwargs)
            ranges[field] = (lo, hi)

    return enabled, ranges


# --------------------------------------------------------------------
# Bundle construction (direction-aware)
# --------------------------------------------------------------------

def build_best_and_worst_inputs(main_inputs, ranges):
    """Return (best_inputs, worst_inputs).

    For each field, pick the min or max based on MDES_DIRECTION so that the
    'best' bundle minimizes MDES and the 'worst' bundle maximizes it.
    Falls back to 'inverse' direction (like sample sizes) for unknown fields.
    """
    best = deepcopy(main_inputs)
    worst = deepcopy(main_inputs)
    for field, (lo, hi) in ranges.items():
        direction = MDES_DIRECTION.get(field, "inverse")
        if direction == "inverse":
            # field ↑ ⇒ MDES ↓  → max is best, min is worst
            best[field] = hi
            worst[field] = lo
        else:  # "direct"
            # field ↑ ⇒ MDES ↑  → min is best, max is worst
            best[field] = lo
            worst[field] = hi
    return best, worst


def run_engine_safe(engine_fn, inputs):
    """Run engine_fn with inputs; return the result object or the ValueError
    message if validation fails. Never raises."""
    try:
        return engine_fn(**inputs)
    except ValueError as e:
        return str(e)


# --------------------------------------------------------------------
# On-screen panel
# --------------------------------------------------------------------

def render_sensitivity_panel(best_result, main_result, worst_result, outcome_type):
    """Render the three-column Best / Main / Worst comparison on screen.
    Engines are assumed to have already been run by the caller."""
    st.subheader("Sensitivity analysis")
    st.caption(
        "MDES under the best case (smallest MDES), the main scenario, and the "
        "worst case (largest MDES). Each bundle mixes parameter mins and maxs "
        "to push MDES in the same direction."
    )

    col_best, col_main, col_worst = st.columns(3)
    _render_mini_card(col_best,  "Best case (smallest MDES)",  best_result,  outcome_type)
    _render_mini_card(col_main,  "Main scenario",              main_result,  outcome_type)
    _render_mini_card(col_worst, "Worst case (largest MDES)",  worst_result, outcome_type)


def _render_mini_card(col, title, result, outcome_type):
    with col:
        st.markdown(f"**{title}**")
        if isinstance(result, str):
            st.error(result)
            return
        st.metric("MDES (standardized)", f"{result.mdes:.4f}")
        if outcome_type == "binary" and result.mdes_pct_points is not None:
            st.metric("MDES (pp)", f"{result.mdes_pct_points:.2f} pp")
        elif result.mdes_standardized is not None:
            st.metric("MDES (raw)", f"{result.mdes_standardized:.4f}")
        st.metric("SE", f"{result.se:.4f}")
        st.metric("df", f"{result.df}")

# services/dynamic_labels.py

"""
Dynamic label generation for calculator inputs.

Labels adapt to:
- the design’s level structure (1–4 levels)
- the assignment unit (individual, cluster, district, etc.)
- whether the design is blocked
- whether the design is RD or ITS
- whether the field is an R², ICC, or sample-size field

This keeps the UI clean, intuitive, and design-specific.
"""

# -------------------------------------------------------------------
# Canonical fallback names for each level
# -------------------------------------------------------------------

LEVEL_NAMES = {
    1: "individual level",
    2: "cluster level",
    3: "third level",
    4: "fourth level",
}

# -------------------------------------------------------------------
# Optional design-specific overrides
# (You can extend this later if you want richer semantics)
# -------------------------------------------------------------------

def get_level_label(level: int, design) -> str:
    """
    Returns the human-readable name for a given level.
    Uses design-specific overrides if present; otherwise falls back.
    """
    # If the design has custom labels (optional future extension)
    if hasattr(design, "level_labels") and design.level_labels:
        if level in design.level_labels:
            return design.level_labels[level]

    # Fallback to canonical names
    return LEVEL_NAMES.get(level, f"level {level}")


# -------------------------------------------------------------------
# Field-specific label logic
# -------------------------------------------------------------------

def dynamic_label(field: str, design) -> str:
    """
    Generate a user-friendly label for a calculator input field,
    based on the design’s structure.
    """

    # -------------------------
    # R² fields
    # -------------------------
    if field.startswith("r2_level"):
        level = int(field[-1])
        level_name = get_level_label(level, design)
        return f"R² at {level_name}"

    # -------------------------
    # ICC
    # -------------------------
    if field == "icc":
        # ICC always refers to level 2 variance
        level_name = get_level_label(2, design)
        return f"ICC ({level_name})"

    # -------------------------
    # Cluster size
    # -------------------------
    if field == "cluster_size":
        level_name = get_level_label(2, design)
        return f"Cluster size ({level_name})"

    # -------------------------
    # Number of clusters
    # -------------------------
    if field == "n_clusters":
        level_name = get_level_label(2, design)
        return f"Number of clusters ({level_name})"

    # -------------------------
    # Number of blocks
    # -------------------------
    if field == "n_blocks":
        return "Number of blocks"

    # -------------------------
    # Treatment probabilities
    # -------------------------
    if field == "p_treat":
        return "Treatment probability"

    if field == "p_block_treat":
        return "Treatment probability within blocks"

    if field == "block_prop":
        return "Block proportion"

    # -------------------------
    # RD-specific fields
    # -------------------------
    if field == "cutoff":
        return "Cutoff value"

    if field == "kernel":
        return "Kernel function"

    if field == "treatment_side":
        return "Treatment side"

    if field == "bandwidth":
        return "Bandwidth"

    if field == "running_var_sd":
        return "Running variable SD"

    # -------------------------
    # ITS-specific fields
    # -------------------------
    if field == "autocorrelation":
        return "Autocorrelation"

    if field == "n_timepoints_pre":
        return "Pre-intervention time points"

    if field == "n_timepoints_post":
        return "Post-intervention time points"

    # -------------------------
    # Outcome fields
    # -------------------------
    if field == "effect_size":
        return "Effect size"

    if field == "baseline_prob":
        return "Baseline probability"

    if field == "outcome_sd_input":
        return "Outcome SD"

    # -------------------------
    # Significance and power
    # -------------------------
    if field == "alpha":
        return "Significance level (α)"

    if field == "power":
        return "Statistical power"

    # -------------------------
    # Fallback: prettify field name
    # -------------------------
    return field.replace("_", " ").title()
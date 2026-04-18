"""
Per-design narrative metadata, keyed by design.code.

Fields
------
design_label : str
    Human-readable description inserted in the Model Definition block.
levels : int
    Number of analytic levels (1-4). Drives which label slots are requested.
params : list[dict]
    Ordered innermost-first. Each dict has:
      key       -- engine parameter name (e.g., "n_level3")
      symbol    -- canonical math symbol ("n", "J", "K", "L")
      unit_slot -- which label this enumerates ("level1"..."level4")
      per_slot  -- "per X" phrase uses this slot (or None for the outermost)
nesting_text : str
    Model Definition block clause describing the nesting structure.
    Uses {level{N}_plural} placeholders.
assignment_text : str
    Model Definition block clause describing where treatment is assigned.
    Uses {level{N}_plural}/{level{N}_singular} placeholders.
random_effects, fixed_effects : list[str]
    Label-slot keys (e.g., "level3_plural") that appear as random/fixed effects.
uses_omega : bool
    If True, the Statistical Assumptions block adds a sentence about ω.
omega_symbol : str
    Symbol used in that sentence (e.g., "ω₃", "ω₄"). Ignored if uses_omega=False.
p_key : str | None
    Input dict key that holds the treatment allocation ratio, or None if the
    engine hardcodes it (then the block uses "p = 0.5").
default_labels : dict[str, str]
    Per-slot defaults (plural form) when the user leaves fields blank.
kind : str
    "multilevel" (default) or "time_series" for ITS — picks the right block
    builders.
"""

MULTILEVEL_DEFAULTS = {
    "level1": "individuals",
    "level2": "clusters",
    "level3": "blocks",
    "level4": "blocks",
}

BCRA4_DEFAULTS = {
    "level1": "individuals",
    "level2": "clusters",
    "level3": "sites",
    "level4": "blocks",
}

BIRA4_DEFAULTS = {
    "level1": "individuals",
    "level2": "clusters",
    "level3": "sites",
    "level4": "blocks",
}


NARRATIVE_SPECS = {
    # ------------------------------------------------------------------
    # IRA
    # ------------------------------------------------------------------
    "IRA": {
        "design_label": "individual-level randomized design",
        "levels": 1,
        "params": [
            {"key": "n_individuals", "symbol": "n", "unit_slot": "level1", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are the sole analytic unit",
        "assignment_text": "directly to individual {level1_plural}",
        "random_effects": [],
        "fixed_effects": [],
        "uses_omega": False,
        "p_key": "p",
        "default_labels": {"level1": "individuals"},
    },

    # ------------------------------------------------------------------
    # BIRA (blocked individual random assignment)
    # ------------------------------------------------------------------
    "BIRA2_1c": {
        "design_label": "2-level blocked individual randomized design with constant block effects",
        "levels": 2,
        "params": [
            {"key": "n_individuals", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_blocks",      "symbol": "J", "unit_slot": "level2", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}",
        "assignment_text": "{level1_plural} within {level2_plural}",
        "random_effects": [],
        "fixed_effects": [],
        "uses_omega": False,
        "p_key": "prop_treated",
        "default_labels": {"level1": "individuals", "level2": "blocks"},
    },
    "BIRA2_1f": {
        "design_label": "2-level blocked individual randomized design with fixed block effects",
        "levels": 2,
        "params": [
            {"key": "n_individuals", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_blocks",      "symbol": "J", "unit_slot": "level2", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}",
        "assignment_text": "{level1_plural} within {level2_plural}",
        "random_effects": [],
        "fixed_effects": ["level2_plural"],
        "uses_omega": False,
        "p_key": None,
        "default_labels": {"level1": "individuals", "level2": "blocks"},
    },
    "BIRA2_1r": {
        "design_label": "2-level blocked individual randomized design with random block effects",
        "levels": 2,
        "params": [
            {"key": "n_individuals", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_blocks",      "symbol": "J", "unit_slot": "level2", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}",
        "assignment_text": "{level1_plural} within {level2_plural}",
        "random_effects": ["level2_plural"],
        "fixed_effects": [],
        "uses_omega": True,
        "omega_symbol": "ω₂",
        "p_key": "prop_treated",
        "default_labels": {"level1": "individuals", "level2": "blocks"},
    },
    "BIRA3_1r": {
        "design_label": "3-level blocked individual randomized design with random blocks",
        "levels": 3,
        "params": [
            {"key": "cluster_size",         "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_clusters_per_block", "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_blocks",             "symbol": "K", "unit_slot": "level3", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are grouped into {level3_plural}",
        "assignment_text": "{level1_plural} within {level2_plural} within {level3_plural}",
        "random_effects": ["level3_plural", "level2_plural"],
        "fixed_effects": [],
        "uses_omega": True,
        "omega_symbol": "ω",
        "p_key": "prop_treated",
        "default_labels": {"level1": "individuals", "level2": "clusters", "level3": "blocks"},
    },
    "BIRA4_1r": {
        "design_label": "4-level blocked individual randomized design with random blocks",
        "levels": 4,
        "params": [
            {"key": "cluster_size",        "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_clusters_per_site", "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_sites_per_block",   "symbol": "K", "unit_slot": "level3", "per_slot": "level4"},
            {"key": "n_blocks",            "symbol": "L", "unit_slot": "level4", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are nested within {level3_plural}, which are grouped into {level4_plural}",
        "assignment_text": "{level1_plural} within {level2_plural} within {level3_plural} within {level4_plural}",
        "random_effects": ["level4_plural", "level3_plural", "level2_plural"],
        "fixed_effects": [],
        "uses_omega": True,
        "omega_symbol": "ω",
        "p_key": "prop_treated",
        "default_labels": BIRA4_DEFAULTS,
    },

    # ------------------------------------------------------------------
    # CRA (cluster random assignment)
    # ------------------------------------------------------------------
    "CRA2_2r": {
        "design_label": "2-level cluster randomized design",
        "levels": 2,
        "params": [
            {"key": "cluster_size", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_clusters",   "symbol": "J", "unit_slot": "level2", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}",
        "assignment_text": "the {level2_singular} level",
        "random_effects": ["level2_plural"],
        "fixed_effects": [],
        "uses_omega": False,
        "p_key": "p_treat",
        "default_labels": {"level1": "individuals", "level2": "clusters"},
    },
    "CRA3_3r": {
        "design_label": "3-level cluster randomized design",
        "levels": 3,
        "params": [
            {"key": "cluster_size", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_level2",     "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_level3",     "symbol": "K", "unit_slot": "level3", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are nested within {level3_plural}",
        "assignment_text": "the {level3_singular} level",
        "random_effects": ["level3_plural", "level2_plural"],
        "fixed_effects": [],
        "uses_omega": False,
        "p_key": "p_treat",
        "default_labels": {"level1": "individuals", "level2": "clusters", "level3": "sites"},
    },
    "CRA4_4r": {
        "design_label": "4-level cluster randomized design",
        "levels": 4,
        "params": [
            {"key": "cluster_size", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_level2",     "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_level3",     "symbol": "K", "unit_slot": "level3", "per_slot": "level4"},
            {"key": "n_level4",     "symbol": "L", "unit_slot": "level4", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are nested within {level3_plural}, which are nested within {level4_plural}",
        "assignment_text": "the {level4_singular} level",
        "random_effects": ["level4_plural", "level3_plural", "level2_plural"],
        "fixed_effects": [],
        "uses_omega": False,
        "p_key": "p_treat",
        "default_labels": BCRA4_DEFAULTS,
    },

    # ------------------------------------------------------------------
    # BCRA (blocked cluster random assignment)
    # ------------------------------------------------------------------
    "BCRA3_2f": {
        "design_label": "3-level blocked cluster randomized design with fixed blocks",
        "levels": 3,
        "params": [
            {"key": "cluster_size", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_level2",     "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_level3",     "symbol": "K", "unit_slot": "level3", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are grouped into {level3_plural}",
        "assignment_text": "the {level2_singular} level within {level3_plural}",
        "random_effects": ["level2_plural"],
        "fixed_effects": ["level3_plural"],
        "uses_omega": False,
        "p_key": None,
        "default_labels": {"level1": "individuals", "level2": "clusters", "level3": "blocks"},
    },
    "BCRA3_2r": {
        "design_label": "3-level blocked cluster randomized design with random blocks",
        "levels": 3,
        "params": [
            {"key": "cluster_size", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_level2",     "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_level3",     "symbol": "K", "unit_slot": "level3", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are grouped into {level3_plural}",
        "assignment_text": "the {level2_singular} level within {level3_plural}",
        "random_effects": ["level3_plural", "level2_plural"],
        "fixed_effects": [],
        "uses_omega": True,
        "omega_symbol": "ω₃",
        "p_key": None,
        "default_labels": {"level1": "individuals", "level2": "clusters", "level3": "blocks"},
    },
    "BCRA4_2r": {
        "design_label": "4-level blocked cluster randomized design with random blocks, assignment at level 2",
        "levels": 4,
        "params": [
            {"key": "cluster_size", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_level2",     "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_level3",     "symbol": "K", "unit_slot": "level3", "per_slot": "level4"},
            {"key": "n_level4",     "symbol": "L", "unit_slot": "level4", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are nested within {level3_plural}, which are grouped into {level4_plural}",
        "assignment_text": "the {level2_singular} level within {level4_plural}",
        "random_effects": ["level4_plural", "level3_plural", "level2_plural"],
        "fixed_effects": [],
        "uses_omega": True,
        "omega_symbol": "ω",
        "p_key": "p_treat",
        "default_labels": BCRA4_DEFAULTS,
    },
    "BCRA4_3f": {
        "design_label": "4-level blocked cluster randomized design with fixed blocks, assignment at level 3",
        "levels": 4,
        "params": [
            {"key": "cluster_size", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_level2",     "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_level3",     "symbol": "K", "unit_slot": "level3", "per_slot": "level4"},
            {"key": "n_level4",     "symbol": "L", "unit_slot": "level4", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are nested within {level3_plural}, which are grouped into {level4_plural}",
        "assignment_text": "the {level3_singular} level within {level4_plural}",
        "random_effects": ["level3_plural", "level2_plural"],
        "fixed_effects": ["level4_plural"],
        "uses_omega": False,
        "p_key": "p_treat",
        "default_labels": BCRA4_DEFAULTS,
    },
    "BCRA4_3r": {
        "design_label": "4-level blocked cluster randomized design with random blocks, assignment at level 3",
        "levels": 4,
        "params": [
            {"key": "cluster_size", "symbol": "n", "unit_slot": "level1", "per_slot": "level2"},
            {"key": "n_level2",     "symbol": "J", "unit_slot": "level2", "per_slot": "level3"},
            {"key": "n_level3",     "symbol": "K", "unit_slot": "level3", "per_slot": "level4"},
            {"key": "n_level4",     "symbol": "L", "unit_slot": "level4", "per_slot": None},
        ],
        "nesting_text": "{level1_plural} are nested within {level2_plural}, which are nested within {level3_plural}, which are grouped into {level4_plural}",
        "assignment_text": "the {level3_singular} level within {level4_plural}",
        "random_effects": ["level4_plural", "level3_plural", "level2_plural"],
        "fixed_effects": [],
        "uses_omega": True,
        "omega_symbol": "ω₄",
        "p_key": "p_treat",
        "default_labels": BCRA4_DEFAULTS,
    },

    # ------------------------------------------------------------------
    # ITS (interrupted time series)
    # ------------------------------------------------------------------
    "ITS": {
        "design_label": "interrupted time series design",
        "kind": "time_series",
        "levels": 1,
        "params": [
            {"key": "n_timepoints_pre",  "symbol": "T_pre",  "unit_slot": "timepoint_pre",  "per_slot": None},
            {"key": "n_timepoints_post", "symbol": "T_post", "unit_slot": "timepoint_post", "per_slot": None},
        ],
        "uses_omega": False,
        "p_key": None,
        "default_labels": {
            "timepoint_pre": "pre-intervention time points",
            "timepoint_post": "post-intervention time points",
        },
    },
}

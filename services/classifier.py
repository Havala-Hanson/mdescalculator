# services/classifier.py

import re
from typing import NamedTuple, List, Tuple
from config.designs import DESIGNS, DESIGN_BY_CODE

# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

class ClassifierResult(NamedTuple):
    design: str
    confidence: float
    top_designs: List[Tuple[str, float]]
    rationale: str
    family_scores: dict[str, float]  


# ─────────────────────────────────────────────────────────────
# Keyword patterns for assignment-unit detection
# ─────────────────────────────────────────────────────────────

_KEYWORDS_L3_RANDOMIZED = [
    r"\bdistricts?\b",
    r"\bhospitals?\b",
    r"\bcount(?:y|ies)\b",
    r"\borganizations?\b",
    r"\bsystems?\b",
    r"\bclinics?\b",
    r"\bcenters?\b",
    r"\blevel[- ]?3\b",
    r"\bthree[- ]?level\b",
    r"\bthird[- ]?level\b",
]

_KEYWORDS_L2_RANDOMIZED = [
    r"\bschools?\b",
    r"\bclassrooms?\b",
    r"\bteachers?\b",
    r"\bsites?\b",
    r"\bclusters?\b",
    r"\bsections?\b",
    r"\bgroups?\b",
    r"\btherapists?\b",
    r"\bproviders?\b",
    r"\bclinicians?\b",
    r"\bcaseworkers?\b",
    r"\binstructors?\b",
    r"\bpractices?\b",
    r"\blocations?\b",
    r"\blevel[- ]?2\b",
    r"\btwo[- ]?level\b",
    r"\bsecond[- ]?level\b",
]

_KEYWORDS_INDIVIDUAL = [
    r"\bindividuals?\b",
    r"\bparticipants?\b",
    r"\bpatients?\b",
    r"\bclients?\b",
    r"\bchildren?\b",
    r"\bchild\b",
    r"\badults?\b",
    r"\byouths?\b",
    r"\bpersons?\b",
    r"\bpeople\b",
    r"\bkids?\b",
    r"random(?:ly assign\w*|iz\w+) (?:individual|participant|patient|client|child|adult|person)\w*",
    r"\brandom assignment of individuals?\b",
]


# ─────────────────────────────────────────────────────────────
# Blocking detection
# ─────────────────────────────────────────────────────────────

_KEYWORDS_BLOCKED = [
    r"\bblocks?\b",
    r"\bstrat\w*\b",
    r"\bstrata\b",
    r"\bstratum\b",
    r"\bcohorts?\b",
    r"\bpaired\b",
    r"\bmatched pairs?\b",
    r"\bblocked by\b",
    r"\bstratified by\b",
    r"\bmatched on\b",
    r"\bwithin-(?:schools?|districts?|teachers?|clinics?|classrooms?|sites?|groups?)\b",
    r"(?:assign\w+|randomiz\w+)\s+(?:\w+\s+)?within",
]


# ─────────────────────────────────────────────────────────────
# Nesting structure detection
# ─────────────────────────────────────────────────────────────

_PATTERNS_NESTING_EXPLICIT = [
    r"\bnested (?:within|in|under)\b",
]

_PATTERNS_NESTING_PARTIAL = [
    r"\bwithin\b",
    r"\bgrouped (?:by|within)\b",
    r"\bclustered (?:in|within)\b",
    r"\bhierarchical\b",
]

# ─────────────────────────────────────────────────────────────
# Quasi-experimental families
# ─────────────────────────────────────────────────────────────

_KEYWORDS_RD = [
    r"\bregression discontinuity\b",
    r"\bcutoff\b",
    r"\bthreshold\b",
    r"\beligibility score\b",
    r"\bassignment rule\b",
]

_KEYWORDS_ITS = [
    r"\binterrupted time series\b",
    r"\btime[- ]series\b",
    r"\bbefore and after\b",
    r"\bpre[- ]intervention\b",
    r"\bpost[- ]intervention\b",
    r"\bpolicy change\b",
    r"\binterruption\b",
]


# ─────────────────────────────────────────────────────────────
# Randomization verb detection
# ─────────────────────────────────────────────────────────────

_PATTERNS_RAND_VERB = [
    r"\brandomly assign",
    r"\brandomiz",
    r"\brandomis",
    r"\brandom allocation\b",
    r"\bassigned at random\b",
]

_PATTERNS_RAND_IMPLIED = [
    r"\ballocated? to\b",
    r"\bassigned? to\b",
    r"\btreatment assigned\b",
]


# ─────────────────────────────────────────────────────────────
# Explicit assignment-unit detection (active + passive voice)
# ─────────────────────────────────────────────────────────────

_PATTERNS_EXPLICIT_L3 = [
    r"random(?:ly assign\w*|iz\w+) (?:district|hospital|county|organization|clinic|center)\w*",
    r"\b(?:districts?|hospitals?|county|counties|clinics?|centers?)\b.{0,20}random(?:ly assign\w*|iz\w+)",
]

_PATTERNS_EXPLICIT_L2 = [
    r"random(?:ly assign\w*|iz\w+) (?:school|classroom|teacher|site|cluster|section|group|therapist|provider|clinician)\w*",
    r"\b(?:schools?|classrooms?|teachers?|sites?|clusters?|sections?|groups?|therapists?|providers?|clinicians?)\b.{0,20}random(?:ly assign\w*|iz\w+)",
]

_PATTERNS_EXPLICIT_IND = [
    r"random(?:ly assign\w*|iz\w+) (?:individual|participant|patient|client|child|adult)\w*",
    r"\b(?:individuals?|participants?|patients?|clients?|children?|adults?)\b.{0,20}random(?:ly assign\w*|iz\w+)",
]


# ─────────────────────────────────────────────────────────────
# Confidence rubric weights
# ─────────────────────────────────────────────────────────────

_CONF_SINGLE_UNIT = 0.5
_CONF_MULTI_UNIT = 0.2
_CONF_NESTING_EXPLICIT = 0.3
_CONF_NESTING_PARTIAL = 0.15
_CONF_BLOCKING = 0.1
_CONF_RAND_VERB = 0.2
_CONF_RAND_IMPLIED = 0.1


# ─────────────────────────────────────────────────────────────
# Rationale builder
# ─────────────────────────────────────────────────────────────

def _build_rationale(
    design: str,
    *,
    explicit_l3: bool,
    explicit_l2: bool,
    explicit_ind: bool,
    has_blocking: bool,
    has_nesting: bool,
    confidence: float | None = None,
) -> str:
    """
    Build a rationale that explains:
    1. Why this design family was selected.
    2. Why other families were not selected.
    3. What information was missing or ambiguous.
    4. How confidence relates to the evidence in the prompt.
    """
    d = DESIGN_BY_CODE.get(design)
    if d is None:
        return "Suggested because the description matched this design most closely."

    parts = []
    ruled_out = []
    missing = []
    guidance = []

    # ----------------------------------------------------------------------
    # 1. Confidence-weighted interpretation
    # ----------------------------------------------------------------------

    if confidence is not None:
        if confidence >= 0.75:
            parts.append("the classifier is highly confident based on strong, consistent signals")
        elif confidence >= 0.45:
            parts.append("the classifier is moderately confident based on several supporting signals")
        else:
            parts.append("the classifier has low confidence because the prompt contained limited or ambiguous information")

    # ----------------------------------------------------------------------
    # 2. Why this family was selected
    # ----------------------------------------------------------------------

    if d.design_family == "IRA":
        parts.append("individual-level randomization language was detected")
        if explicit_ind:
            parts.append("with explicit references to randomizing individuals")

    elif d.design_family == "BIRA":
        parts.append("individual-level randomization within blocks was detected")
        if not has_blocking:
            missing.append("clear blocking or stratification language")
        if explicit_ind:
            parts.append("with explicit individual randomization language")

    elif d.design_family == "CRA":
        parts.append("cluster-level randomization was detected")
        if explicit_l2 or explicit_l3:
            parts.append("with explicit references to randomizing clusters or higher-level units")

    elif d.design_family == "BCRA":
        parts.append("cluster-level randomization within blocks was detected")
        if not has_blocking:
            missing.append("stronger blocking or stratification language")
        if explicit_l2 or explicit_l3:
            parts.append("with explicit cluster-level randomization language")

    elif d.design_family == "RD":
        parts.append("cutoff or threshold-based assignment language was detected")
        parts.append("which is characteristic of regression discontinuity designs")

    elif d.design_family == "ITS":
        parts.append("longitudinal before/after or time-series structure was detected")
        parts.append("which is characteristic of interrupted time series designs")

    # ----------------------------------------------------------------------
    # 3. Variant-level rationale (levels, blocking, assignment unit)
    # ----------------------------------------------------------------------

    # Levels
    if d.levels == 1:
        parts.append("the study appears to involve only one level of analysis")
    elif d.levels == 2:
        parts.append("the study appears to involve two levels (e.g., individuals nested in clusters)")
    elif d.levels == 3:
        parts.append("the study appears to involve three levels of nesting")
    elif d.levels == 4:
        parts.append("the study appears to involve four levels of nesting")

    # Assignment unit
    if d.assignment_unit == "individual":
        parts.append("treatment appears to be assigned to individuals")
    elif d.assignment_unit == "cluster":
        parts.append("treatment appears to be assigned to clusters (e.g., classrooms, schools, clinics)")
    elif d.assignment_unit == "district":
        parts.append("treatment appears to be assigned at a higher organizational level")

    # Blocking
    if d.is_blocked:
        parts.append("the description suggested blocking or stratification")
    else:
        if has_blocking:
            ruled_out.append("blocked designs were considered but the overall pattern matched an unblocked structure")

    # Nesting
    if has_nesting:
        parts.append("the description referenced nested or hierarchical structure")

    # Block effect structure
    if d.block_effect:
        parts.append(f"the design variant uses {d.block_effect} block effects")
    else:
        if d.is_blocked:
            missing.append("whether block effects were constant, fixed, or random")

    # ----------------------------------------------------------------------
    # 4. Why other families were not selected
    # ----------------------------------------------------------------------

    if d.design_family in ("IRA", "BIRA", "CRA", "BCRA"):
        ruled_out.append("quasi-experimental families (RD, ITS) were ruled out because no cutoff or time-series structure was detected")

    if d.design_family == "RD":
        ruled_out.append("randomized designs were ruled out because no randomization language appeared")

    if d.design_family == "ITS":
        ruled_out.append("randomized and cutoff-based designs were ruled out because the description emphasized longitudinal structure")

    # ----------------------------------------------------------------------
    # 5. Missing or ambiguous information (diagnostics)
    # ----------------------------------------------------------------------

    if d.assignment_unit == "individual" and not explicit_ind:
        missing.append("explicit individual-level assignment language")

    if d.assignment_unit == "cluster" and not (explicit_l2 or explicit_l3):
        missing.append("explicit cluster-level assignment language")

    if d.levels >= 3 and not has_nesting:
        missing.append("clear nesting structure (e.g., classrooms within schools)")

    # ----------------------------------------------------------------------
    # 6. Guidance for improving the prompt
    # ----------------------------------------------------------------------

    if missing:
        guidance.append(
            "To strengthen classification, consider specifying: "
            + "; ".join(missing)
        )

    if d.design_family in ("BIRA", "BCRA") and not has_blocking:
        guidance.append("If blocking is present, mention the grouping variable (e.g., 'within schools', 'within districts').")

    if d.design_family == "RD" and not explicit_ind and not explicit_l2:
        guidance.append("For RD designs, specifying the assignment variable and cutoff improves accuracy.")

    if d.design_family == "ITS" and not has_nesting:
        guidance.append("For ITS designs, mentioning the number of time points helps distinguish ITS from simple pre/post designs.")

    # ----------------------------------------------------------------------
    # Assemble final rationale
    # ----------------------------------------------------------------------

    rationale_parts = []

    if parts:
        rationale_parts.append("Suggested because " + "; ".join(parts) + ".")

    if ruled_out:
        rationale_parts.append("Other designs were ruled out because " + "; ".join(ruled_out) + ".")

    if guidance:
        rationale_parts.append("To improve classification, " + " ".join(guidance))

    return " ".join(rationale_parts)

# ─────────────────────────────────────────────────────────────
# Design selection heuristics within families
# ─────────────────────────────────────────────────────────────

def _select_design_from_family(
    family: str,
    *,
    is_blocked: bool,
    levels_hint: int | None,
    assignment_unit_hint: str | None,
) -> str:
    """Pick a specific design code within a family using simple heuristics."""
    candidates = [d for d in DESIGNS if d.design_family == family]

    # Blocked vs simple
    blocked_filtered = [d for d in candidates if d.is_blocked == is_blocked]
    if blocked_filtered:
        candidates = blocked_filtered

    # Levels
    if levels_hint is not None:
        level_filtered = [d for d in candidates if d.levels == levels_hint]
        if level_filtered:
            candidates = level_filtered

    # Assignment unit
    if assignment_unit_hint is not None:
        unit_filtered = [d for d in candidates if d.assignment_unit == assignment_unit_hint]
        if unit_filtered:
            candidates = unit_filtered

    # Fallback: first candidate
    return candidates[0].code

# ─────────────────────────────────────────────────────────────
# Main classifier
# ─────────────────────────────────────────────────────────────

def classify_study(description: str) -> ClassifierResult:
    text = description.lower()

    def count_hits(patterns: List[str]) -> int:
        return sum(1 for pat in patterns if re.search(pat, text))

    def has_match(patterns: List[str]) -> bool:
        return any(re.search(pat, text) for pat in patterns)

    hits_l3 = count_hits(_KEYWORDS_L3_RANDOMIZED)
    hits_l2 = count_hits(_KEYWORDS_L2_RANDOMIZED)
    hits_blocked = count_hits(_KEYWORDS_BLOCKED)
    hits_individual = count_hits(_KEYWORDS_INDIVIDUAL)

    # Explicit assignment-unit patterns
    explicit_l3 = has_match(_PATTERNS_EXPLICIT_L3)
    explicit_l2 = has_match(_PATTERNS_EXPLICIT_L2)
    explicit_ind = has_match(_PATTERNS_EXPLICIT_IND)

    # --- FAMILY-LEVEL SCORING ---

    has_rd = has_match(_KEYWORDS_RD)
    has_its = has_match(_KEYWORDS_ITS)

    scores_family = {
        "IRA": 0.0,
        "BIRA": 0.0,
        "CRA": 0.0,
        "BCRA": 0.0,
        "RD": 0.0,
        "ITS": 0.0,
    }

    # RD / ITS dominate if detected
    if has_rd:
        scores_family["RD"] += 3.0
    if has_its:
        scores_family["ITS"] += 3.0

    # Individual randomized
    if hits_individual > 0 and not has_rd and not has_its:
        scores_family["IRA"] += hits_individual
        if hits_blocked > 0:
            scores_family["BIRA"] += hits_individual + hits_blocked

    # Cluster randomized
    if (hits_l2 > 0 or hits_l3 > 0) and not has_rd and not has_its:
        scores_family["CRA"] += hits_l2 + hits_l3
        if hits_blocked > 0:
            scores_family["BCRA"] += hits_l2 + hits_l3 + hits_blocked

    # Normalize
    total_family = sum(scores_family.values()) or 1.0
    scores_family = {k: v / total_family for k, v in scores_family.items()}

    # Pick best family
    best_family, best_family_score = max(scores_family.items(), key=lambda x: x[1])

    # Derive hints for selecting specific design
    is_blocked_flag = hits_blocked > 0

    levels_hint = None
    if hits_l3 > 0 and hits_l2 > 0:
        levels_hint = 3
    elif hits_l2 > 0:
        levels_hint = 2

    assignment_unit_hint = None
    if hits_individual > 0 and not has_rd:
        assignment_unit_hint = "individual"
    elif hits_l2 > 0 or hits_l3 > 0:
        assignment_unit_hint = "cluster"

    # Pick specific design from family
    best_design = _select_design_from_family(
        best_family,
        is_blocked=is_blocked_flag,
        levels_hint=levels_hint,
        assignment_unit_hint=assignment_unit_hint,
    )

    confidence = 0.0

    num_explicit = int(explicit_l3) + int(explicit_l2) + int(explicit_ind)
    if num_explicit == 1:
        confidence += _CONF_SINGLE_UNIT
    elif num_explicit > 1:
        confidence += _CONF_MULTI_UNIT
    elif hits_l3 > 0 or hits_l2 > 0:
        confidence += _CONF_MULTI_UNIT

    if has_match(_PATTERNS_NESTING_EXPLICIT):
        confidence += _CONF_NESTING_EXPLICIT
    elif has_match(_PATTERNS_NESTING_PARTIAL):
        confidence += _CONF_NESTING_PARTIAL

    if hits_blocked > 0:
        confidence += _CONF_BLOCKING

    if has_match(_PATTERNS_RAND_VERB):
        confidence += _CONF_RAND_VERB
    elif has_match(_PATTERNS_RAND_IMPLIED):
        confidence += _CONF_RAND_IMPLIED

    if hits_individual > hits_l2 and hits_individual > hits_l3 and best_design != "INDIV_RCT":
        confidence *= 0.3

    confidence = min(1.0, confidence)

    rationale = _build_rationale(
        best_design,
        explicit_l3=explicit_l3,
        explicit_l2=explicit_l2,
        explicit_ind=explicit_ind,
        has_blocking=hits_blocked > 0,
        has_nesting=(
            has_match(_PATTERNS_NESTING_EXPLICIT)
            or has_match(_PATTERNS_NESTING_PARTIAL)
        ),
        confidence=confidence,
    )


    return ClassifierResult(
        design=best_design,
        confidence=confidence,
        top_designs=[(best_design, best_family_score)],
        rationale=rationale,
        family_scores=scores_family, 
    )


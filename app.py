"""
MDES Calculator – Landing page.

This module implements the main landing page of the MDES Calculator app,
including:
- Hero section with a brief description
- Design-selection tiles
- Guided questionnaire for users unsure of their design
- Natural-language study description with a rules-based classifier
"""

from __future__ import annotations

import re
from typing import NamedTuple

import streamlit as st

# ── Page configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="MDES Calculator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design catalogue ──────────────────────────────────────────────────────────

class DesignInfo(NamedTuple):
    code: str
    title: str
    description: str
    icon: str
    page: str
    levels: int


DESIGNS: list[DesignInfo] = [
    DesignInfo(
        code="CRA2_2",
        title="Two-level cluster randomized assignment, treatment at the cluster level",
        description=(
            "Whole classrooms or schools are randomly assigned to treatment "
            "or control.  Students are nested within clusters."
        ),
        icon="🏫",
        page="pages/1_Two_Level_CRT.py",
        levels=2,
    ),
    DesignInfo(
        code="BCRA2_2",
        title="Two-level blocked cluster randomized assignment, treatment at the cluster level",
        description=(
            "Classrooms are randomly assigned within predefined blocks "
            "(e.g., grade levels, geographic regions, or cohorts)."
        ),
        icon="🧩",
        page="pages/3_Blocked_Design.py",
        levels=2,
    ),
    DesignInfo(
        code="CRA3_3",
        title="Three-level cluster randomized assignment, treatment at the district level",
        description=(
            "Top-level organizations (districts, hospitals, counties) are "
            "randomly assigned.  Schools and students are nested below."
        ),
        icon="🏙️",
        page="pages/2_Three_Level_CRT.py",
        levels=3,
    ),
    DesignInfo(
        code="BCRA3_2",
        title="Three-level blocked cluster randomized assignment, treatment at the school level",
        description=(
            "Schools are randomly assigned to treatment within districts. "
            "Districts serve as blocks; students are nested within schools."
        ),
        icon="🏢",
        page="pages/2_Three_Level_CRT.py",
        levels=3,
    ),
]

# Keywords for the rules-based classifier
_KEYWORDS_L3_RANDOMIZED = [
    r"\bdistricts?\b", r"\bhospitals?\b", r"\bcounty\b", r"\bcounties\b",
    r"\borganizat", r"\bsystems?\b", r"\blevel.?3\b", r"\bthree.level\b",
    r"\bclinics?\b", r"\bcenters?\b",
]
_KEYWORDS_L2_RANDOMIZED = [
    r"\bschools?\b", r"\bclassrooms?\b", r"\bteachers?\b",
    r"\bsites?\b", r"\bclusters?\b", r"\blevel.?2\b", r"\btwo.level\b",
    r"\bsections?\b", r"\bgroups?\b", r"\btherapists?\b", r"\bproviders?\b",
    r"\bclinicians?\b", r"\bcaseworkers?\b", r"\binstructors?\b",
]
_KEYWORDS_BLOCKED = [
    r"\bblocks?\b", r"\bstrat", r"\bcohorts?\b", r"\bpaired\b",
    r"\bblocked by\b", r"\bstratified by\b", r"\bmatched on\b",
    r"\bwithin-sites?\b", r"\bwithin-schools?\b", r"\bwithin-districts?\b",
    r"\bwithin-teachers?\b", r"\bwithin-clinics?\b",
    r"(?:assign\w+|randomiz\w+)\s+(?:\w+\s+)?within",
]
_KEYWORDS_INDIVIDUAL = [
    r"\bindividuals?\b", r"\bparticipants?\b", r"\bpatients?\b",
    r"\bperson.level\b", r"\bclients?\b", r"\bchild(?:ren)?\b",
    r"\badults?\b", r"\byouths?\b",
    r"random(?:ly assign\w*|iz\w+) (?:individual|participant|patient|client|child|adult)\w*",
]

# Patterns for randomization verb detection (confidence rubric)
_PATTERNS_RAND_VERB = [
    r"\brandomly assign", r"\brandomiz", r"\brandomis",
]
_PATTERNS_RAND_IMPLIED = [
    r"\ballocated? to\b", r"\bassigned? to\b", r"\btreatment assigned\b",
]

# Patterns for explicit assignment-unit detection (confidence rubric and
# design scoring tie-breaking). Covers active voice ("randomly assigning
# schools") and passive voice ("schools are randomly assigned").
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

# Patterns for nesting structure detection (confidence rubric)
_PATTERNS_NESTING_EXPLICIT = [
    r"\bnested (?:within|in)\b",
]
_PATTERNS_NESTING_PARTIAL = [
    r"\bwithin\b", r"\bgrouped (?:by|within)\b", r"\bclustered (?:in|within)\b",
]

# Confidence rubric weights (additive, capped at 1.0)
_CONF_SINGLE_UNIT = 0.5      # single clearly identified assignment unit
_CONF_MULTI_UNIT = 0.2       # multiple possible units, or unit implied by keywords
_CONF_NESTING_EXPLICIT = 0.3 # explicit nesting phrase ("nested within")
_CONF_NESTING_PARTIAL = 0.15 # partial nesting signal ("within")
_CONF_BLOCKING = 0.1         # blocking keywords detected
_CONF_RAND_VERB = 0.2        # explicit randomization verb
_CONF_RAND_IMPLIED = 0.1     # implied assignment language


# ── Classifier ────────────────────────────────────────────────────────────────

class ClassifierResult(NamedTuple):
    design: str
    confidence: float
    top_designs: list[tuple[str, float]]
    rationale: str = ""


def _build_rationale(
    design: str,
    *,
    explicit_l3: bool,
    explicit_l2: bool,
    has_blocking: bool,
    has_nesting: bool,
) -> str:
    """Return a one-sentence rationale for the recommended design."""
    reasons: dict[str, str] = {
        "CRA3_3": "district- or organization-level randomization was detected",
        "BCRA3_2": (
            "school-level randomization within districts (blocking) was detected"
            if has_blocking
            else "school-level randomization with a higher-level grouping structure was detected"
        ),
        "CRA2_2": "classroom- or site-level randomization without blocking was detected",
        "BCRA2_2": "classroom-level randomization within pre-existing blocks was detected",
    }
    base = reasons.get(design, "the description matched this design most closely")
    if has_nesting:
        base += ", with an explicit nesting structure"
    return f"Suggested because {base}."


def classify_study(description: str) -> ClassifierResult:
    """Classify a free-text study description into an MDES design code.

    This is a lightweight rules-based classifier that scores descriptions
    against keyword patterns.  It returns a confidence score in [0, 1] and
    recommends one or more designs.

    Confidence is computed via an additive rubric (see module-level pattern
    constants) based on: explicit assignment-unit detection, nesting structure,
    blocking keywords, and presence of a randomization verb.

    Parameters
    ----------
    description:
        Free-text study description entered by the user.

    Returns
    -------
    ClassifierResult
        Best-match design code, its confidence score, the top-3 designs
        with scores, and a one-sentence rationale.
    """
    text = description.lower()

    def count_hits(patterns: list[str]) -> int:
        return sum(1 for pat in patterns if re.search(pat, text))

    def has_match(patterns: list[str]) -> bool:
        return any(re.search(pat, text) for pat in patterns)

    hits_l3 = count_hits(_KEYWORDS_L3_RANDOMIZED)
    hits_l2 = count_hits(_KEYWORDS_L2_RANDOMIZED)
    hits_blocked = count_hits(_KEYWORDS_BLOCKED)
    hits_individual = count_hits(_KEYWORDS_INDIVIDUAL)

    total = max(hits_l3 + hits_l2 + hits_blocked + hits_individual, 1)

    scores: dict[str, float] = {
        "CRA3_3": hits_l3 / total,
        "BCRA3_2": (hits_l3 + hits_blocked) / (2 * total),
        "CRA2_2": hits_l2 / total,
        "BCRA2_2": (hits_l2 + hits_blocked) / (2 * total),
    }

    # Penalise cluster designs when individual-randomization language dominates
    if hits_individual > hits_l2 and hits_individual > hits_l3:
        for key in scores:
            scores[key] *= 0.3

    # Boost blocked designs when blocking keywords are found
    if hits_blocked > 0:
        scores["BCRA3_2"] *= 1.5
        scores["BCRA2_2"] *= 1.5

    # Extra boost for BCRA3_2 when both L2 and L3 keywords appear alongside
    # blocking – this is the classic "schools within districts" pattern.
    if hits_l3 > 0 and hits_l2 > 0 and hits_blocked > 0:
        scores["BCRA3_2"] *= 2.0

    # ── Explicit assignment-unit boosts ──────────────────────────────────────
    # Detect explicit assignment patterns (active and passive voice).
    # These are also used later by the confidence rubric.
    explicit_l3 = has_match(_PATTERNS_EXPLICIT_L3)
    explicit_l2 = has_match(_PATTERNS_EXPLICIT_L2)
    explicit_ind = has_match(_PATTERNS_EXPLICIT_IND)

    # Boost the design that best matches the explicitly stated assignment unit.
    if explicit_l3 and hits_blocked == 0:
        scores["CRA3_3"] *= 2.0       # districts/hospitals assigned, no blocking
    if explicit_l2:
        if hits_blocked > 0 and hits_l3 == 0:
            scores["BCRA2_2"] *= 2.0  # clusters assigned within non-district blocks
        elif hits_blocked == 0 and hits_l3 == 0:
            scores["CRA2_2"] *= 2.0   # pure two-level cluster design

    # Normalise
    total_score = sum(scores.values()) or 1.0
    scores = {k: v / total_score for k, v in scores.items()}

    sorted_designs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_design, _ = sorted_designs[0]

    # ── Rubric-based confidence scoring ──────────────────────────────────────
    # Start at 0.0 and accumulate up to 1.0 based on signal strength.

    confidence = 0.0

    # 1. Assignment unit detection (max +_CONF_SINGLE_UNIT)
    # explicit_l3, explicit_l2, explicit_ind computed during design scoring above.
    num_explicit = int(explicit_l3) + int(explicit_l2) + int(explicit_ind)

    if num_explicit == 1:
        confidence += _CONF_SINGLE_UNIT    # single clear assignment unit
    elif num_explicit > 1:
        confidence += _CONF_MULTI_UNIT     # multiple possible units
    elif hits_l3 > 0 or hits_l2 > 0:
        confidence += _CONF_MULTI_UNIT     # assignment unit implied by keywords

    # 2. Nesting structure detection (max +_CONF_NESTING_EXPLICIT)
    if has_match(_PATTERNS_NESTING_EXPLICIT):
        confidence += _CONF_NESTING_EXPLICIT   # explicit "nested within" phrasing
    elif has_match(_PATTERNS_NESTING_PARTIAL):
        confidence += _CONF_NESTING_PARTIAL    # partial nesting signal (e.g., "within")

    # 3. Blocking detection (max +_CONF_BLOCKING)
    if hits_blocked > 0:
        confidence += _CONF_BLOCKING

    # 4. Randomization verb detection (max +_CONF_RAND_VERB)
    if has_match(_PATTERNS_RAND_VERB):
        confidence += _CONF_RAND_VERB          # explicit randomization verb
    elif has_match(_PATTERNS_RAND_IMPLIED):
        confidence += _CONF_RAND_IMPLIED       # implied assignment language

    # 5. Reduce confidence when individual-randomization language dominates
    if hits_individual > hits_l2 and hits_individual > hits_l3:
        confidence *= 0.3

    # Cap at 1.0
    confidence = min(1.0, confidence)

    rationale = _build_rationale(
        best_design,
        explicit_l3=explicit_l3,
        explicit_l2=explicit_l2,
        has_blocking=hits_blocked > 0,
        has_nesting=(
            has_match(_PATTERNS_NESTING_EXPLICIT)
            or has_match(_PATTERNS_NESTING_PARTIAL)
        ),
    )

    return ClassifierResult(
        design=best_design,
        confidence=confidence,
        top_designs=sorted_designs[:3],
        rationale=rationale,
    )


# ── UI helpers ────────────────────────────────────────────────────────────────

def design_card(design: DesignInfo, key_prefix: str) -> bool:
    """Render a design tile card.

    Returns ``True`` if the user clicked the 'Use this design' button.
    """
    with st.container(border=True):
        st.markdown(f"### {design.icon} {design.title}")
        st.caption(f"**Technical code:** `{design.code}`")
        st.write(design.description)
        return st.button(
            "Use this design →",
            key=f"{key_prefix}_{design.code}",
            type="primary",
        )


# Threshold for "high confidence" single-design recommendation.
# With the rubric-based scoring (max 1.0), a score >= 0.7 indicates that at
# least a clear assignment unit and nesting or blocking signal were detected.
_HIGH_CONFIDENCE_THRESHOLD = 0.7

# Help text shown when the user clicks "Something else — add more detail"
_CLASSIFIER_HELP_TEXT = (
    "💡 **Tips for a better match:** Try including details such as:\n"
    "- How many levels of nesting your study has "
    "(e.g., *students nested within schools nested within districts*)\n"
    "- What unit is randomly assigned "
    "(e.g., *schools are randomly assigned to treatment*)\n"
    "- Whether randomization occurs within pre-existing groupings or blocks\n\n"
    "Edit your description above and the classifier will update automatically."
)


def confidence_badge(confidence: float) -> str:
    """Format a confidence value as a colour-coded badge string."""
    if confidence >= _HIGH_CONFIDENCE_THRESHOLD:
        return f"🟢 High confidence ({confidence:.0%})"
    elif confidence >= 0.4:
        return f"🟡 Moderate confidence ({confidence:.0%})"
    else:
        return f"🔴 Low confidence ({confidence:.0%})"


# ── Page layout ───────────────────────────────────────────────────────────────

# ── Hero ──────────────────────────────────────────────────────────────────────
st.title("🔬 MDES Calculator")
st.subheader("Minimum Detectable Effect Size for Multilevel Randomized Trials")
st.write(
    "This tool helps education, medical, public-health, psychology, and "
    "social-science researchers determine the smallest effect their study "
    "design can reliably detect.  Select your study design below, or use the "
    "classifier to identify your design from a plain-language description."
)
st.divider()

# ── Design tiles ──────────────────────────────────────────────────────────────
st.header("📐 Select your study design")
st.write(
    "Choose the design that best matches how your study randomizes "
    "participants.  Each tile shows a plain-language description and its "
    "technical code."
)

cols = st.columns(2)
for idx, design in enumerate(DESIGNS):
    with cols[idx % 2]:
        clicked = design_card(design, key_prefix="tile")
        if clicked:
            page_map = {
                "CRA2_2": "pages/1_Two_Level_CRT",
                "BCRA2_2": "pages/3_Blocked_Design",
                "CRA3_3": "pages/2_Three_Level_CRT",
                "BCRA3_2": "pages/2_Three_Level_CRT",
            }
            target = page_map.get(design.code, "pages/1_Two_Level_CRT")
            st.session_state["selected_design"] = design.code
            st.switch_page(target)

st.divider()

# ── Guided questionnaire ──────────────────────────────────────────────────────
with st.expander("🧭 Not sure which design fits? Take the guided questionnaire"):
    st.write("Answer these questions to identify your design.")

    q1 = st.radio(
        "1. What is the **unit of randomization** in your study?",
        options=[
            "Individuals (people are individually assigned)",
            "Small groups / classrooms / clinics",
            "Schools / hospitals / organizations",
            "Districts / large systems",
        ],
        index=None,
        key="q1",
    )

    q2 = st.radio(
        "2. Are there **blocking factors** (pre-existing groups within which "
        "randomization occurs, e.g., grade levels, geographic regions)?",
        options=["Yes, there are blocks", "No, it is a simple random assignment"],
        index=None,
        key="q2",
    )

    if q1 and q2:
        is_blocked = q2.startswith("Yes")
        if "Individuals" in q1:
            st.info(
                "ℹ️ Individual-level randomization is not a cluster design.  "
                "This tool focuses on cluster randomized trials.  You may want "
                "a standard power calculator for individually randomized studies."
            )
        elif "Small groups" in q1 or "classrooms" in q1.lower():
            rec = "BCRA2_2" if is_blocked else "CRA2_2"
            d = next(d for d in DESIGNS if d.code == rec)
            st.success(f"✅ Recommended design: **{d.title}** (`{rec}`)")
            if st.button("Open this calculator", key="guided_open"):
                st.session_state["selected_design"] = rec
                if rec == "BCRA2_2":
                    st.switch_page("pages/3_Blocked_Design")
                else:
                    st.switch_page("pages/1_Two_Level_CRT")
        elif "Schools" in q1 or "hospitals" in q1.lower():
            rec = "BCRA3_2" if is_blocked else "CRA2_2"
            d = next(d for d in DESIGNS if d.code == rec)
            st.success(f"✅ Recommended design: **{d.title}** (`{rec}`)")
            if st.button("Open this calculator", key="guided_open2"):
                st.session_state["selected_design"] = rec
                if rec == "BCRA3_2":
                    st.switch_page("pages/2_Three_Level_CRT")
                else:
                    st.switch_page("pages/1_Two_Level_CRT")
        else:
            rec = "CRA3_3"
            d = next(d for d in DESIGNS if d.code == rec)
            st.success(f"✅ Recommended design: **{d.title}** (`{rec}`)")
            if st.button("Open this calculator", key="guided_open3"):
                st.session_state["selected_design"] = rec
                st.switch_page("pages/2_Three_Level_CRT")

st.divider()

# ── Natural-language classifier ───────────────────────────────────────────────
st.header("💬 Describe your study in plain language")
st.write(
    "Type a brief description of your study design (e.g., *'We are randomly "
    "assigning schools within districts to receive a new math curriculum.  "
    "Students are nested within schools.'*).  The classifier will suggest a "
    "design for you."
)

nl_input = st.text_area(
    "Study description",
    placeholder="Describe your study here…",
    height=120,
    key="nl_description",
)

if nl_input and len(nl_input.strip()) > 10:
    result = classify_study(nl_input)
    st.markdown(f"**Classification result:** {confidence_badge(result.confidence)}")

    if result.confidence >= _HIGH_CONFIDENCE_THRESHOLD:
        matched_design = next(
            (d for d in DESIGNS if d.code == result.design), None
        )
        if matched_design:
            st.success(
                f"Recommended design: **{matched_design.title}** "
                f"(`{result.design}`)"
            )
            if result.rationale:
                st.caption(result.rationale)
            if st.button("Open recommended calculator", key="nl_open"):
                st.session_state["selected_design"] = result.design
                page_map = {
                    "CRA2_2": "pages/1_Two_Level_CRT",
                    "BCRA2_2": "pages/3_Blocked_Design",
                    "CRA3_3": "pages/2_Three_Level_CRT",
                    "BCRA3_2": "pages/2_Three_Level_CRT",
                }
                st.switch_page(page_map[result.design])
    else:
        st.warning(
            "The classifier is not confident about your design.  "
            "Here are the top matches:"
        )
        top_cols = st.columns(3)
        for col_idx, (code, score) in enumerate(result.top_designs):
            matched = next((d for d in DESIGNS if d.code == code), None)
            if matched:
                with top_cols[col_idx]:
                    with st.container(border=True):
                        st.markdown(f"**{matched.icon} {matched.title}**")
                        st.caption(f"`{code}` — score {score:.0%}")
                        if st.button("Select", key=f"nl_select_{code}"):
                            st.session_state["selected_design"] = code
                            page_map = {
                                "CRA2_2": "pages/1_Two_Level_CRT",
                                "BCRA2_2": "pages/3_Blocked_Design",
                                "CRA3_3": "pages/2_Three_Level_CRT",
                                "BCRA3_2": "pages/2_Three_Level_CRT",
                            }
                            st.switch_page(page_map[code])

        st.write("")
        if st.button(
            "Something else — add more detail",
            key="nl_something_else",
            type="secondary",
        ):
            st.session_state["nl_show_hint"] = True

        if st.session_state.get("nl_show_hint"):
            st.info(_CLASSIFIER_HELP_TEXT)

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(
    "MDES Calculator · MIT License · "
    "Formulas based on Bloom et al. (2007) and Dong & Maynard (2013)."
)

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
    r"\bdistrict\b", r"\bhospital\b", r"\bcounty\b", r"\borganizat",
    r"\bsystem\b", r"\blevel.?3\b", r"\bthree.level\b",
    r"randomized? (district|hospital|county|organization)",
]
_KEYWORDS_L2_RANDOMIZED = [
    r"\bschool\b", r"\bclassroom\b", r"\bteacher\b", r"\bclinic\b",
    r"\bsite\b", r"\bcluster\b", r"\blevel.?2\b", r"\btwo.level\b",
    r"randomized? (school|classroom|teacher|clinic|site|cluster)",
]
_KEYWORDS_BLOCKED = [
    r"\bblock\b", r"\bstrat", r"\bwithin.site\b", r"\bwithin.school\b",
    r"\bwithin.district\b", r"\bcohort\b", r"\bpaired\b",
]
_KEYWORDS_INDIVIDUAL = [
    r"\bindividual\b", r"\bparticipant\b", r"\bpatient\b",
    r"\bperson.level\b", r"randomized? individual",
]


# ── Classifier ────────────────────────────────────────────────────────────────

"""
Classifier requirements for natural-language study descriptions.

The classifier must reliably detect:
1. UNIT OF RANDOMIZATION (assignment)
   - Keywords for individuals: student, participant, patient, client, child, adult
   - Keywords for level-2 clusters: classroom, section, group, therapist, provider
   - Keywords for level-3 clusters: teacher, clinician, caseworker
   - Keywords for level-4 clusters: school, clinic, hospital, site, district
   - Keywords for blocking: within, stratified by, blocked by, matched on

2. NESTING STRUCTURE (levels)
   - Detect phrases like “students nested within classrooms”, “patients nested within clinics”
   - If both a lower-level and higher-level unit appear, infer levels:
       individuals → clusters → sites
   - If only individuals + clusters appear, infer 2-level structure.

3. ASSIGNMENT LOGIC
   - If the text says “randomly assigning X”, X is the unit of assignment.
   - If the text says “randomizing within Y”, Y is the blocking variable.
   - If the text says “randomizing individuals within sites”, classify as multi-site RCT.

4. DESIGN MAPPING RULES
   - If assignment unit is individuals → Individual Randomized Trial (IRT)
   - If assignment unit is a level-2 cluster → Two-level cluster randomized assignment (treatment at cluster level)
   - If assignment unit is a level-3 cluster → Three-level cluster randomized assignment (treatment at level 3)
   - If assignment unit is a level-2 cluster AND blocking is detected → Blocked cluster randomized assignment
   - If assignment unit is individuals AND sites are mentioned → Multi-site randomized assignment (individuals randomized within sites)
   - If assignment unit is clusters AND sites are mentioned → Multi-site cluster randomized assignment

5. CONFIDENCE SCORING
   - Confidence increases when:
       - assignment unit is explicitly named (“we are randomly assigning schools”)
       - nesting structure is explicit (“students nested within schools”)
       - blocking is explicit (“within teachers”, “within clinics”)
   - Confidence decreases when:
       - multiple possible assignment units appear
       - nesting structure is ambiguous
       - no randomization verb is detected

   - If top confidence >= 0.7 → return ONE recommended design.
   - If top confidence < 0.7 → return TOP THREE designs + “something else” option.

6. OUTPUT FORMAT
   For each design returned:
   - descriptive_name: plain-language label (primary)
   - technical_name: PowerUpR-style label (secondary)
   - rationale: one sentence explaining why it was suggested

7. EXAMPLE CLASSIFICATION
   Input:
       “We are randomly assigning schools within districts to receive a new math curriculum.
        Students are nested within schools.”
   Expected:
       descriptive_name: “Three-level cluster randomized assignment, treatment at the school level”
       technical_name: “CRA3_3”
       rationale: “You described randomizing schools, with students nested within schools and districts above them.”
       confidence: high (>= 0.7)

8. Leverage a keyword dictionary for units, nesting, blocking, and randomization verbs. The dictionary gives the classifier a vocabulary for detecting the unit of assignment, nesting structure, presence of blocking, whether the design is multi-site, and whether the text even describes randomization.  
KEYWORDS = {
    "individual": [
        "student", "students", "participant", "participants", "patient", "patients",
        "client", "clients", "child", "children", "adult", "adults", "youth"
    ],
    "cluster_level_2": [
        "classroom", "classrooms", "section", "sections", "group", "groups",
        "cohort", "cohorts", "therapist", "therapists", "provider", "providers"
    ],
    "cluster_level_3": [
        "teacher", "teachers", "clinician", "clinicians", "caseworker", "caseworkers",
        "instructor", "instructors"
    ],
    "cluster_level_4": [
        "school", "schools", "clinic", "clinics", "hospital", "hospitals",
        "site", "sites", "district", "districts", "center", "centers"
    ],
    "nesting": [
        "nested within", "within", "inside", "under", "grouped by", "clustered in"
    ],
    "blocking": [
        "within", "blocked by", "stratified by", "matched on", "paired with"
    ],
    "randomization": [
        "randomly assigning", "randomly assigned", "randomizing", "randomised",
        "assigned to", "allocated to", "treatment assigned at"
    ],
    "multi_site": [
        "within sites", "across sites", "multi-site", "multi site", "across clinics",
        "across schools", "across districts"
    ]
}

    9. Confidence scoring rubric for classification. This rubric gives explicit rules for how to assign confidence scores. It prevents the classifier from returning low-quality guesses and ensures that clear cases like school-level randomization get high confidence. 

Confidence scoring rubric:

Start with a base confidence of 0.0 and add points based on detected features.

1. Assignment unit detection (max +0.5)
   - If a single assignment unit is clearly identified (e.g., "randomly assigning schools"): +0.5
   - If multiple possible assignment units appear: +0.2
   - If no assignment unit is detected: +0.0

2. Nesting structure detection (max +0.3)
   - If explicit nesting is detected (e.g., "students nested within schools"): +0.3
   - If partial nesting is detected (e.g., "students in schools"): +0.15
   - If no nesting structure is detected: +0.0

3. Blocking detection (max +0.1)
   - If blocking keywords appear (e.g., "within teachers", "blocked by school"): +0.1

4. Multi-site detection (max +0.1)
   - If multi-site keywords appear (e.g., "within sites", "across clinics"): +0.1

5. Randomization verb detection (max +0.2)
   - If a clear randomization verb appears (e.g., "randomly assigning"): +0.2
   - If assignment is implied but not explicit: +0.1

Total possible confidence: 1.2 (cap at 1.0)

Threshold rule:
- If top design confidence >= 0.7 → return ONE recommended design.
- If top design confidence < 0.7 → return TOP THREE designs + “something else” option.

10. Mapping rules for design classification
These rules tell exactly how to map detected units and nesting to the correct design. THe mapping ensures that "schools within districts" -> three-level custer randomized assignment, treatment at school level; "classrooms within teachers" -> blocked cluster randomized assignment, "students within sites" -> multi-site individual randomized assignment, etc. 

Design mapping rules:

1. Individual randomized trial (IRT)
   - Assignment unit: individual
   - Nesting: optional
   - Multi-site: optional

2. Two-level cluster randomized assignment (treatment at cluster level)
   - Assignment unit: level-2 cluster (classrooms, sections, groups)
   - Nesting: individuals → clusters
   - No blocking detected

3. Blocked cluster randomized assignment
   - Assignment unit: level-2 cluster
   - Blocking detected (e.g., "within teachers")

4. Three-level cluster randomized assignment (treatment at level 3)
   - Assignment unit: level-3 cluster (teachers, clinicians)
   - Nesting: individuals → level-2 → level-3

5. Three-level cluster randomized assignment (treatment at level 4)
   - Assignment unit: level-4 cluster (schools, clinics, districts)
   - Nesting: individuals → level-2 → level-3 → level-4

6. Multi-site individual randomized assignment (MRT)
   - Assignment unit: individuals
   - Multi-site keywords detected

7. Multi-site cluster randomized assignment
   - Assignment unit: clusters (level-2 or level-3)
   - Multi-site keywords detected

"""

class ClassifierResult(NamedTuple):
    design: str
    confidence: float
    top_designs: list[tuple[str, float]]


def classify_study(description: str) -> ClassifierResult:
    """Classify a free-text study description into an MDES design code.

    This is a lightweight rules-based classifier that scores descriptions
    against keyword patterns.  It returns a confidence score in [0, 1] and
    recommends one or more designs.

    Parameters
    ----------
    description:
        Free-text study description entered by the user.

    Returns
    -------
    ClassifierResult
        Best-match design code, its confidence score, and the top-3 designs
        with scores.
    """
    text = description.lower()

    def count_hits(patterns: list[str]) -> int:
        return sum(1 for pat in patterns if re.search(pat, text))

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

    # Penalise individual-randomization designs (not CRT)
    if hits_individual > hits_l2 and hits_individual > hits_l3:
        for key in scores:
            scores[key] *= 0.3

    # Boost blocked designs when blocking keywords found
    if hits_blocked > 0:
        scores["BCRA3_2"] *= 1.5
        scores["BCRA2_2"] *= 1.5

    # Normalise
    total_score = sum(scores.values()) or 1.0
    scores = {k: v / total_score for k, v in scores.items()}

    sorted_designs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_design, best_conf = sorted_designs[0]

    # Clamp confidence to [0.1, 0.95]
    confidence = max(0.1, min(0.95, best_conf))

    return ClassifierResult(
        design=best_design,
        confidence=confidence,
        top_designs=sorted_designs[:3],
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
# The keyword-scoring formula has a mathematical maximum of ~66.7% (when
# only one category of keyword patterns fires and none from other categories),
# so a threshold above that value would never be reached.
_HIGH_CONFIDENCE_THRESHOLD = 0.6

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

# MDES Calculator – Landing page.
#
# This module implements the main landing page of the MDES Calculator app,
# including:
# - Hero section with a brief description
# - Design-selection tiles
# - Guided questionnaire for users unsure of their design
# - Natural-language study description with a rules-based classifier

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
        title="Classrooms (or schools) randomized",
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
        title="Classrooms randomized within sites",
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
        title="Districts (or large organizations) randomized",
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
        title="Schools randomized within districts",
        description=(
            "Schools are randomly assigned to treatment within districts. "
            "Districts serve as blocks; students are nested within schools."
        ),
        icon="🏢",
        page="pages/2_Three_Level_CRT.py",
        levels=3,
    ),
]

# Map from design code to page path (derived from DESIGNS to avoid duplication)
_PAGE_MAP: dict[str, str] = {d.code: d.page for d in DESIGNS}

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


def confidence_badge(confidence: float) -> str:
    """Format a confidence value as a colour-coded badge string."""
    if confidence >= 0.7:
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
            st.session_state["selected_design"] = design.code
            st.switch_page(_PAGE_MAP.get(design.code, "pages/1_Two_Level_CRT.py"))

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
                    st.switch_page("pages/3_Blocked_Design.py")
                else:
                    st.switch_page("pages/1_Two_Level_CRT.py")
        elif "Schools" in q1 or "hospitals" in q1.lower():
            rec = "BCRA3_2" if is_blocked else "CRA2_2"
            d = next(d for d in DESIGNS if d.code == rec)
            st.success(f"✅ Recommended design: **{d.title}** (`{rec}`)")
            if st.button("Open this calculator", key="guided_open2"):
                st.session_state["selected_design"] = rec
                if rec == "BCRA3_2":
                    st.switch_page("pages/2_Three_Level_CRT.py")
                else:
                    st.switch_page("pages/1_Two_Level_CRT.py")
        else:
            rec = "CRA3_3"
            d = next(d for d in DESIGNS if d.code == rec)
            st.success(f"✅ Recommended design: **{d.title}** (`{rec}`)")
            if st.button("Open this calculator", key="guided_open3"):
                st.session_state["selected_design"] = rec
                st.switch_page("pages/2_Three_Level_CRT.py")

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

    if result.confidence >= 0.7:
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
                st.switch_page(_PAGE_MAP[result.design])
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
                            st.switch_page(_PAGE_MAP[code])
        with top_cols[-1] if len(result.top_designs) < 3 else st.container():
            st.info(
                "None of these match?  Use the guided questionnaire above or "
                "select a design tile manually."
            )

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(
    "MDES Calculator · MIT License · "
    "Formulas based on Bloom et al. (2007) and Dong & Maynard (2013)."
)

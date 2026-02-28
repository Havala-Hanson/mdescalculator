import streamlit as st
from config.designs import DESIGNS, DESIGN_BY_CODE, PAGE_BY_CODE

st.title("Guided Study Design Questionnaire")
st.write(
    "Answer a few short questions and we’ll narrow down the study design that "
    "matches your description. If you're unsure about a question, use the (i) "
    "icons or expanders for examples."
)

# ─────────────────────────────────────────────────────────────
# Helper: filter designs by metadata fields
# ─────────────────────────────────────────────────────────────

def filter_designs(designs, **criteria):
    result = designs
    for field, value in criteria.items():
        if value is None:
            continue
        result = [d for d in result if getattr(d, field) == value]
    return result


remaining = DESIGNS

# ─────────────────────────────────────────────────────────────
# Q1: Randomized vs non-randomized
# ─────────────────────────────────────────────────────────────

q1 = st.radio(
    "Is treatment assignment randomized?",
    ["Yes", "No"],
    index=None,
    help=(
        "Choose **Yes** if units are assigned to treatment by chance. "
        "Choose **No** if assignment is based on a cutoff, rule, timing, "
        "or natural variation (e.g., regression discontinuity or time-series)."
    ),
)

if q1:
    remaining = filter_designs(remaining, is_randomized=(q1 == "Yes"))

    if q1 == "No":
        with st.expander("Examples of non-randomized designs"):
            st.write(
                "- **Regression Discontinuity (RD):** assignment based on a score threshold.\n"
                "- **Interrupted Time Series (ITS):** repeated measurements before and after an intervention.\n"
                "- **Matched comparison:** assignment not random but based on natural groups."
            )

# Stop early if only one design remains
if len(remaining) == 1:
    d = remaining[0]
    st.success(f"Recommended design: **{d.title}** (`{d.code}`)")
    if st.button("Open this calculator"):
        st.switch_page(d.page)
    st.stop()


# ─────────────────────────────────────────────────────────────
# Q2: Unit of assignment
# ─────────────────────────────────────────────────────────────

if len(remaining) > 1:
    q2 = st.radio(
        "What is the **unit of assignment**?",
        ["Individual", "Cluster (classrooms, schools, clinics)", "District / system"],
        index=None,
        help=(
            "This is the level at which treatment is assigned. "
            "Example: If whole schools are assigned, the unit is 'Cluster'."
        ),
    )

    if q2:
        if q2.startswith("Individual"):
            remaining = filter_designs(remaining, assignment_unit="individual")
        elif q2.startswith("Cluster"):
            remaining = filter_designs(remaining, assignment_unit="cluster")
        else:
            remaining = filter_designs(remaining, assignment_unit="district")

        with st.expander("Examples of assignment units"):
            st.write(
                "- **Individual:** students, patients, participants.\n"
                "- **Cluster:** classrooms, schools, clinics, providers.\n"
                "- **District/system:** districts, hospital systems, counties."
            )

if len(remaining) == 1:
    d = remaining[0]
    st.success(f"Recommended design: **{d.title}** (`{d.code}`)")
    if st.button("Open this calculator"):
        st.switch_page(d.page)
    st.stop()


# ─────────────────────────────────────────────────────────────
# Q3: Levels of clustering
# ─────────────────────────────────────────────────────────────

if len(remaining) > 1:
    q3 = st.radio(
        "How many **levels** are in your data structure?",
        ["1", "2", "3", "4"],
        index=None,
        help="Levels reflect nesting. Example: Students → Classrooms → Schools = 3 levels.",
    )

    if q3:
        remaining = filter_designs(remaining, levels=int(q3))

        with st.expander("Examples of levels"):
            st.write(
                "- **1 level:** individuals only.\n"
                "- **2 levels:** individuals nested in clusters (e.g., students in classrooms).\n"
                "- **3 levels:** individuals → clusters → higher clusters (e.g., students → classrooms → schools).\n"
                "- **4 levels:** individuals → classrooms → schools → districts."
            )

if len(remaining) == 1:
    d = remaining[0]
    st.success(f"Recommended design: **{d.title}** (`{d.code}`)")
    if st.button("Open this calculator"):
        st.switch_page(d.page)
    st.stop()


# ─────────────────────────────────────────────────────────────
# Q4: Blocking (randomized designs only)
# ─────────────────────────────────────────────────────────────

if len(remaining) > 1 and remaining[0].is_randomized:
    q4 = st.radio(
        "Is the randomization **blocked or stratified**?",
        ["Yes", "No"],
        index=None,
        help="Blocking means randomization occurs within pre-existing groups (e.g., grade levels, districts).",
    )

    if q4:
        remaining = filter_designs(remaining, is_blocked=(q4 == "Yes"))

        with st.expander("Examples of blocking"):
            st.write(
                "- Randomizing classrooms **within schools**.\n"
                "- Randomizing schools **within districts**.\n"
                "- Randomizing providers **within clinics**."
            )

if len(remaining) == 1:
    d = remaining[0]
    st.success(f"Recommended design: **{d.title}** (`{d.code}`)")
    if st.button("Open this calculator"):
        st.switch_page(d.page)
    st.stop()


# ─────────────────────────────────────────────────────────────
# Q5: Block effect structure (only if blocked)
# ─────────────────────────────────────────────────────────────

if len(remaining) > 1 and any(d.is_blocked for d in remaining):
    q5 = st.radio(
        "How are block effects treated?",
        ["Constant", "Fixed", "Random"],
        index=None,
        help=(
            "This affects how block differences are modeled. "
            "If you're unsure, choose 'Random'—it's the most common."
        ),
    )

    if q5:
        remaining = filter_designs(remaining, block_effect=q5.lower())

        with st.expander("What do these mean?"):
            st.write(
                "- **Constant:** blocks differ by a constant shift.\n"
                "- **Fixed:** each block gets its own intercept.\n"
                "- **Random:** blocks are sampled from a population."
            )

if len(remaining) == 1:
    d = remaining[0]
    st.success(f"Recommended design: **{d.title}** (`{d.code}`)")
    if st.button("Open this calculator"):
        st.switch_page(d.page)
    st.stop()


# ─────────────────────────────────────────────────────────────
# Q6: Quasi-experimental branching (RD vs ITS)
# ─────────────────────────────────────────────────────────────

if len(remaining) > 1 and not remaining[0].is_randomized:
    q6 = st.radio(
        "Which best describes the assignment mechanism?",
        [
            "Cutoff or threshold (Regression Discontinuity)",
            "Longitudinal before/after pattern (Interrupted Time Series)",
        ],
        index=None,
        help="Choose the option that best matches how treatment is assigned.",
    )

    if q6:
        if q6.startswith("Cutoff"):
            remaining = filter_designs(remaining, requires_cutoff=True)
        else:
            remaining = filter_designs(remaining, requires_time_series=True)

        with st.expander("Examples"):
            st.write(
                "- **RD:** Students with scores ≥ 70 receive treatment.\n"
                "- **ITS:** Monthly outcomes measured before and after a policy change."
            )

if len(remaining) == 1:
    d = remaining[0]
    st.success(f"Recommended design: **{d.title}** (`{d.code}`)")
    if st.button("Open this calculator"):
        st.switch_page(d.page)
    st.stop()


# ─────────────────────────────────────────────────────────────
# Final fallback (should rarely happen)
# ─────────────────────────────────────────────────────────────

if len(remaining) > 1:
    st.warning(
        "Multiple designs still match your answers. "
        "Try refining your responses or provide more detail."
    )
    st.write("Remaining candidates:")
    for d in remaining:
        st.write(f"- **{d.title}** (`{d.code}`)")
import streamlit as st
from config.designs import DESIGNS, DESIGN_BY_CODE

st.set_page_config(page_title="MDES Calculator", layout="wide")

# ------------------------------------------------------------
# Family colors (soft pastel backgrounds)
# ------------------------------------------------------------
FAMILY_COLORS = {
    "IRA": "#e6f2ff",
    "BIRA": "#f0e6ff",
    "CRA": "#e6ffe6",
    "BCRA": "#e6fffa",
    "RD": "#fff2e6",
    "ITS": "#ffe6f2",
}

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.title("Minimum Detectable Effect Size (MDES) Calculator")
st.write(
    "Choose a design using the guided assistant below, or jump directly to the full list of designs."
)

# ------------------------------------------------------------
# Quick link for advanced users
# ------------------------------------------------------------
st.markdown("### 🔗 Already know your design?")
st.markdown("[Jump to the full list of designs](#all-designs)", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------------------------
# Find My Design (placeholder)
# ------------------------------------------------------------
st.header("Find my design")
st.write("Answer a few quick questions and we’ll identify the design that matches your study structure.")

with st.expander("Open the design assistant"):
    st.info("Design assistant coming soon — classifier integration will go here.")

st.markdown("---")

# ------------------------------------------------------------
# Featured designs
# ------------------------------------------------------------
st.header("Featured designs")

featured = [d for d in DESIGNS if d.featured]

if featured:
    for d in featured:
        st.subheader(d.title)
        st.write(d.description)
        if st.button(f"Use this design →", key=f"featured_{d.code}"):
            st.switch_page(d.page)
else:
    st.write("No featured designs configured.")

st.markdown("---")

# ------------------------------------------------------------
# Search bar
# ------------------------------------------------------------
st.header("All designs")
st.markdown('<a name="all-designs"></a>', unsafe_allow_html=True)

search_query = st.text_input(
    "Search designs",
    placeholder="Search by keyword, family, or description..."
).lower()

# ------------------------------------------------------------
# Group designs by family
# ------------------------------------------------------------
families = {}
for d in DESIGNS:
    families.setdefault(d.design_family, []).append(d)

# ------------------------------------------------------------
# Render families with color-coded expanders + details panel
# ------------------------------------------------------------
for family in sorted(families.keys()):

    # Filter designs by search
    filtered_designs = [
        d for d in families[family]
        if search_query in d.description.lower()
        or search_query in d.title.lower()
        or search_query in d.code.lower()
        or search_query in family.lower()
    ]

    if not filtered_designs:
        continue

    # Color-coded expander header
    color = FAMILY_COLORS.get(family, "#FFFFFF")
    expander_html = f"""
        <div style="background-color:{color}; padding:8px; border-radius:6px; margin-bottom:4px;">
            <strong>{family}</strong>
        </div>
    """
    st.markdown(expander_html, unsafe_allow_html=True)

    with st.expander("", expanded=False):
        for d in filtered_designs:

            # Row with description + button
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{d.description}**")
            with col2:
                if st.button("Use this design", key=f"use_{d.code}"):
                    st.switch_page(d.page)

            # Details panel
            with st.expander("View details", expanded=False):

                st.markdown(f"**Design code:** {d.code}")
                st.markdown(f"**Assignment unit:** {d.assignment_unit}")
                st.markdown(f"**Assignment level:** {d.assignment_level}")
                st.markdown(f"**Number of levels:** {d.levels}")
                st.markdown(f"**Blocked:** {'Yes' if d.is_blocked else 'No'}")
                if d.is_blocked:
                    st.markdown(f"**Block effect:** {d.block_effect}")

                st.markdown(f"**Randomized:** {'Yes' if d.is_randomized else 'No'}")
                st.markdown(f"**Quasi-experimental:** {'Yes' if d.is_quasi_experimental else 'No'}")

                if d.requires_cutoff:
                    st.markdown("**Requires cutoff:** Yes")
                if d.requires_pre_post:
                    st.markdown("**Requires pre/post:** Yes")
                if d.requires_time_series:
                    st.markdown("**Requires time series:** Yes")
                if d.requires_cluster_assignment:
                    st.markdown("**Requires cluster assignment:** Yes")

                # Model sketch
                model_forms = {
                    "IRA": "Yᵢ = β₀ + δTᵢ + eᵢ",
                    "BIRA": "Yᵢb = β₀ + δTᵢb + γ_b + eᵢb",
                    "CRA": "Yᵢⱼ = β₀ + δTⱼ + uⱼ + eᵢⱼ",
                    "BCRA": "Yᵢⱼb = β₀ + δTⱼb + γ_b + uⱼb + eᵢⱼb",
                    "RD": "Yᵢ = β₀ + δ·1(Xᵢ ≥ c) + f(Xᵢ) + eᵢ",
                    "ITS": "Yₜ = β₀ + β₁·timeₜ + δ·postₜ + eₜ",
                }
                st.markdown(f"**Model form:** `{model_forms.get(d.design_family, '')}`")

                # Typical use cases
                st.markdown("**Typical use cases:**")
                if d.design_family == "IRA":
                    st.write("- Individual-level interventions without clustering.")
                elif d.design_family == "BIRA":
                    st.write("- Individual-level interventions randomized within blocks such as cohorts or sites.")
                elif d.design_family == "CRA":
                    st.write("- Cluster-level interventions such as school- or clinic-level randomization.")
                elif d.design_family == "BCRA":
                    st.write("- Cluster-level interventions with blocking by site, district, or cohort.")
                elif d.design_family == "RD":
                    st.write("- Assignment based on a cutoff in a running variable.")
                elif d.design_family == "ITS":
                    st.write("- Longitudinal administrative or observational data with a clear intervention point.")

                # Key assumptions
                st.markdown("**Key assumptions:**")
                if d.design_family in ["IRA", "BIRA"]:
                    st.write("- Independence of individual outcomes within blocks.")
                if d.design_family in ["CRA", "BCRA"]:
                    st.write("- Independence of clusters; correct specification of cluster-level variance.")
                if d.design_family == "RD":
                    st.write("- Correct functional form near the cutoff; no manipulation of the running variable.")
                if d.design_family == "ITS":
                    st.write("- Stable pre-intervention trend; correct autocorrelation structure.")

                # Action button inside details
                if st.button("Use this design", key=f"details_use_{d.code}"):
                    st.switch_page(d.page)
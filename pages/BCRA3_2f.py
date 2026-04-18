# pages/BCRA3_2f.py

import streamlit as st
from config.designs import DESIGN_BY_CODE
from mdes_engines.bcra import compute_mdes_bcra3_2f
from services.calculator_template import render_calculator_page


DESIGN_CODE = "BCRA3_2f"
design = DESIGN_BY_CODE[DESIGN_CODE]


def render_inputs(design, outcome_type):
    baseline_prob = None
    if outcome_type == "binary":
        baseline_prob = st.number_input(
            "Baseline probability",
            min_value=0.0,
            max_value=1.0,
            value=0.50,
            step=0.01,
            key="baseline_prob_input"
        )

    # -----------------------------
    # Test settings
    # -----------------------------
    alpha = st.number_input(
        "Significance level (α)",
        min_value=0.001,
        max_value=0.20,
        value=0.05,
        step=0.01,
        help="Power is the probability of correctly rejecting the null hypothesis when there is a true effect. Common values are 0.80 (80% power) or 0.90 (90% power). Higher power requires larger sample sizes.",
    )

    power = st.number_input(
        "Power (1 - β)",
        min_value=0.50,
        max_value=0.99,
        value=0.80,
        step=0.05,
        help="Power is the probability of correctly rejecting the null hypothesis when there is a true effect. Common values are 0.80 (80% power) or 0.90 (90% power). Higher power requires larger sample sizes.",
    )

    two_tailed = st.radio(
        "Two-tailed or one-tailed test?",
        options=[True, False],
        format_func=lambda x: "Two‑tailed" if x else "One‑tailed",
        index=0,
        help = "Two-tailed tests are more conservative and test for effects in both directions. One-tailed tests have more power to detect an effect in a specified direction but cannot detect effects in the opposite direction. Default: Two-tailed.",
    )
    
    # -----------------------------
    # Three-level structure
    # -----------------------------
    n_level3 = st.number_input(
        "Number of level-3 blocks (K)",
        min_value=1,
        value=50,
        step=1,
        help="Number of level-3 blocks (e.g., schools). Blocks are fixed effects in this design, so increasing K increases the number of randomized clusters (K × J), which improves power. Default: 50." 
        )

    n_level2 = st.number_input(
        "Number of level-2 units per block (J)",
        min_value=3,
        value=5,
        step=1,
        help="Number of level-2 units (e.g., classrooms) within each block. Increasing J increases the number of randomized units (K × J), which generally improves power, with diminishing returns when ICC2 is high. Default: 5."
        )

    cluster_size = st.number_input(
        "Average number of level-1 units per level-2 unit (n)",
        min_value=1,
        value=30,
        step=1,
        help="Average number of level-1 units (e.g., individuals) per level-2 unit. Larger cluster sizes reduce the within-cluster variance component, improving power, though gains diminish when ICC2 is high. Default: 30."
        )

    # -----------------------------
    # ICCs
    # -----------------------------

    icc2 = st.number_input(
        "ICC (level 2)",
        min_value=0.0,
        max_value=0.99,
        value=0.10,
        step=0.01,
        help="Intraclass correlation at level 2 (e.g., classrooms). Represents the proportion of total variance that is between level-2 units. Higher ICCs typically require larger sample sizes to achieve the same power. Default: 0.10.",
    )

    # -----------------------------
    # Covariates
    # -----------------------------
    r2_level1 = st.number_input(
        "R² (level-1 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Average number of level-1 units (e.g., individuals) per level-2 unit. Larger cluster sizes reduce the within-cluster variance component, improving power, though gains diminish when ICC2 is high. Default: 30."
        )

    r2_level2 = st.number_input(
        "R² (level-2 covariates)",
        min_value=0.0,
        max_value=0.99,
        value=0.0,
        step=0.05,
        help="Proportion of level-2 (cluster-level) variance explained by covariates. Higher values reduce between-cluster variance and lower the MDES. Default: 0.0."
        )

    
    # -----------------------------
    # Return engine inputs
    # -----------------------------
    return {
        "n_level3": n_level3,
        "n_level2": n_level2,
        "cluster_size": cluster_size,
        "icc2": icc2,
        "r2_level1": r2_level1,
        "r2_level2": r2_level2,
        "alpha": alpha,
        "power": power,
        "two_tailed": two_tailed,
        "outcome_type": outcome_type,
        "baseline_prob": baseline_prob,
    }

def render():
    # 1. Render header at the very top
    hdr = design.calculator_header
    st.header(f"{hdr['icon']} {hdr['title']}")
    st.subheader(hdr["subtitle"])
    st.markdown(hdr["description"])

    with st.expander("Statistical background"):
        st.markdown(
            "**Structure:**  Three levels: individuals (1) within clusters (2) within blocks (3). "
            "Clusters are randomized within blocks; block effects are fixed. Assignment at level 2.\n\n"
            "**Key formulas:**\n\n"
        )
        st.markdown(r"- **Variance**")
        st.latex(
            r"""
            \operatorname{Var}(\hat{\delta}) =
            \left[
            \frac{\rho_2(1 - R^2_2)}{P(1-P)\,K\,J}
            + \frac{(1 - \rho_2)(1 - R^2_1)}{P(1-P)\,K\,J\,n}
            \right]
            \cdot \frac{K}{K - 1}
            """
        )
        st.markdown("- **Degrees of freedom:**")
        st.latex(r"\text{df} = K(J - 1) - 1")
        st.markdown(
            "- **Adjustment for covariates:** R-squared for levels 1 and 2 reduce between- "
            "and within-cluster variance; with the finite-block correction:"
        )
        st.latex(r"\frac{K}{K-1}")

    st.markdown("---")

    # Move outcome_type selection outside the form for dynamic rendering
    outcome_type = st.radio(
        "Outcome type",
        options=["continuous", "binary"],
        index=0,
        horizontal=True,
        key="outcome_type_radio",
        help="Select the type of outcome variable. This will determine whether you need to input a baseline probability (for binary outcomes) or an outcome standard deviation (for continuous outcomes). Default: Continuous.",
    )

    st. session_state["outcome_type"] = outcome_type

    #st.markdown("---")

    def input_render_fn(design):
        return render_inputs(design, outcome_type)
    render_calculator_page(
        design=design,
        input_render_fn=input_render_fn,
        engine_fn=compute_mdes_bcra3_2f,
        sensitivity_fields=["n_level3", "n_level2", "cluster_size", "icc2", "r2_level1", "r2_level2"],
    )

render()
# services/export.py

import math
from datetime import datetime


# ------------------------------------------------------------
# Kraft (2019) effect-size thresholds for education research
# ------------------------------------------------------------
def classify_effect_size_kraft(d):
    if d < 0.05:
        return "small"
    elif d < 0.20:
        return "medium"
    else:
        return "large"


# ------------------------------------------------------------
# Percentile-shift interpretation for continuous outcomes
# ------------------------------------------------------------
def percentile_shift(d):
    """
    Convert an effect size into a percentile shift using the normal CDF.
    Returns (new_percentile, shift).
    """
    phi = 0.5 * (1 + math.erf(d / math.sqrt(2)))
    shift = (phi - 0.5) * 100
    return phi * 100, shift


# ------------------------------------------------------------
# Main export builder
# ------------------------------------------------------------
def build_mdes_report(design, inputs, result):
    """
    Build a clean, reproducible text summary of MDES inputs, outputs,
    interpretation, and calculation narrative.
    """

    lines = []

    # ------------------------------------------------------------
    # Header
    # ------------------------------------------------------------
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"MDES Report for {design.title} ({design.code})")
    lines.append(f"Generated on: {timestamp}")
    lines.append("-" * 60)
    lines.append("")

    # ------------------------------------------------------------
    # Inputs
    # ------------------------------------------------------------
    lines.append("Inputs:")
    for k, v in inputs.items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    # ------------------------------------------------------------
    # Results
    # ------------------------------------------------------------
    lines.append("Results:")
    lines.append(f"- MDES (standardized): {result.mdes}")
    lines.append(f"- Standard error: {result.se}")
    lines.append(f"- Degrees of freedom: {result.df}")
    lines.append(f"- Design effect: {result.design_effect}")
    lines.append(f"- Effective sample size: {result.effective_n}")
    lines.append(f"- Total sample size: {result.total_n}")

    if result.mdes_raw is not None:
        lines.append(f"- MDES (raw units): {result.mdes_raw}")

    if result.mdes_pct_points is not None:
        lines.append(f"- MDES (percentage points): {result.mdes_pct_points}")

    lines.append("")

    # ------------------------------------------------------------
    # Interpretation (continuous vs binary)
    # ------------------------------------------------------------
    is_binary = inputs.get("outcome_type") == "binary"

    if not is_binary:
        # Continuous outcome interpretation
        effect_label = classify_effect_size_kraft(result.mdes)
        new_pct, shift = percentile_shift(result.mdes)

        lines.append("Interpretation:")
        lines.append(
            f"Under the assumptions specified, this study is powered to detect an "
            f"effect size of {result.mdes:.3f} standard deviations. Effects of this "
            f"magnitude are considered {effect_label} in education research, based on "
            f"Kraft (2019). An effect of this size would move an average individual "
            f"from the 50th percentile in the control group to approximately the "
            f"{new_pct:.1f}th percentile in the treatment group—a shift of "
            f"{shift:.1f} percentile points. If the true effect is at least this large, "
            f"the study has an {inputs.get('power', '80%')} chance of detecting it at "
            f"the {inputs.get('alpha', '0.05')} significance level."
        )
        lines.append("")

    else:
        # Binary outcome interpretation
        p = inputs.get("baseline_prob")
        mdes_pp = result.mdes_pct_points

        if mdes_pp is None:
            # fallback if calculator didn't compute percentage points
            mdes_pp = result.mdes * (p * (1 - p)) ** 0.5 * 100

        relative_change = (mdes_pp / 100) / p * 100

        lines.append("Interpretation:")
        lines.append(
            f"Under the assumptions specified, this study is powered to detect a "
            f"minimum effect of {mdes_pp:.2f} percentage points above the baseline "
            f"rate of {p*100:.1f}%. This corresponds to a {relative_change:.1f}% "
            f"relative change in the outcome rate. If the true effect is at least "
            f"this large, the study has an {inputs.get('power', '80%')} chance of "
            f"detecting it at the {inputs.get('alpha', '0.05')} significance level. "
            f"Smaller changes in the outcome rate may not be reliably detected."
        )
        lines.append("")

    # ------------------------------------------------------------
    # Calculation narrative
    # ------------------------------------------------------------
    lines.append("How this MDES was calculated:")
    
    lines.append(
        f"The MDES was computed using the {design.title} design ({design.code}), "
        f"which assumes {design.assignment_unit}-level assignment and a "
        f"{design.levels}-level data structure. The calculation used the inputs "
        f"listed above, assumes equal treatment allocation, and applies a "
        f"two-tailed test with α={inputs.get('alpha', 0.05)} and "
        f"power={inputs.get('power', 0.80)}. Variance components and covariate "
        f"adjustments were incorporated according to the design's statistical model. "
        f"For continuous outcomes, effect-size interpretation follows Kraft (2019)."
    )
    lines.append("")

    # ------------------------------------------------------------
    # Design metadata
    # ------------------------------------------------------------
    lines.append("Design metadata:")
    lines.append(f"- Design family: {design.design_family}")
    lines.append(f"- Randomized: {design.is_randomized}")
    lines.append(f"- Blocked: {design.is_blocked}")
    lines.append(f"- Number of levels: {design.levels}")
    if design.is_blocked:
        lines.append(f"- Block effect structure: {design.block_effect}")
    lines.append("")

    return "\n".join(lines)
# services/interpretation.py

import math


# ------------------------------------------------------------
# Kraft (2019) effect-size thresholds
# ------------------------------------------------------------
def classify_effect_size_kraft(d: float) -> str:
    if d < 0.05:
        return "small"
    elif d < 0.20:
        return "medium"
    else:
        return "large"


# ------------------------------------------------------------
# Percentile shift for continuous outcomes
# ------------------------------------------------------------
def percentile_shift(d: float):
    """
    Convert an effect size into a percentile shift using the normal CDF.
    Returns (new_percentile, shift).
    """
    phi = 0.5 * (1 + math.erf(d / math.sqrt(2)))
    shift = (phi - 0.5) * 100
    return phi * 100, shift


# ------------------------------------------------------------
# Unified interpretation builder
# ------------------------------------------------------------
def interpret_mdes(
    mdes: float,
    outcome_type: str,
    baseline_prob: float | None,
    alpha: float,
    power: float
):
    """
    Returns a dict with:
      - label (small/medium/large for continuous)
      - narrative (full paragraph)
      - percentile info (continuous only)
      - binary info (binary only)
    """

    if outcome_type == "continuous":
        label = classify_effect_size_kraft(mdes)
        new_pct, shift = percentile_shift(mdes)

        narrative = (
            f"Under the assumptions specified, this study is powered to detect an "
            f"effect size of {mdes:.3f} standard deviations. Effects of this "
            f"magnitude are considered {label} in education research, based on "
            f"Kraft (2019). An effect of this size would move an average individual "
            f"from the 50th percentile in the control group to approximately the "
            f"{new_pct:.1f}th percentile in the treatment group—a shift of "
            f"{shift:.1f} percentile points. If the true effect is at least this large, "
            f"the study has an {power} chance of detecting it at the {alpha} "
            f"significance level."
        )

        return {
            "label": label,
            "narrative": narrative,
            "new_percentile": new_pct,
            "percentile_shift": shift,
            "mdes_pct_points": None,
            "relative_change": None,
        }

    # --------------------------------------------------------
    # Binary outcome interpretation
    # --------------------------------------------------------
    if outcome_type == "binary":
        if baseline_prob is None:
            raise ValueError("baseline_prob is required for binary outcomes.")

        mdes_pp = mdes * 100
        relative_change = (mdes_pp / 100) / baseline_prob * 100

        narrative = (
            f"Under the assumptions specified, this study is powered to detect a "
            f"minimum effect of {mdes_pp:.2f} percentage points above the baseline "
            f"rate of {baseline_prob*100:.1f}%. This corresponds to a "
            f"{relative_change:.1f}% relative change in the outcome rate. If the "
            f"true effect is at least this large, the study has an {power} chance "
            f"of detecting it at the {alpha} significance level."
        )

        return {
            "label": None,
            "narrative": narrative,
            "new_percentile": None,
            "percentile_shift": None,
            "mdes_pct_points": mdes_pp,
            "relative_change": relative_change,
        }

    raise ValueError("Unknown outcome_type.")
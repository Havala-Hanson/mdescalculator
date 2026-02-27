"""Tests for the rules-based classifier in app.py."""
from __future__ import annotations

import sys
from unittest.mock import MagicMock


def _import_app():
    """Import app.py with streamlit mocked out."""
    st_mock = MagicMock()
    st_mock.set_page_config = MagicMock()
    sys.modules.setdefault("streamlit", st_mock)

    import importlib
    import app  # noqa: PLC0415
    importlib.reload(app)
    return app


_app = _import_app()
classify_study = _app.classify_study
ClassifierResult = _app.ClassifierResult


# ── Basic design detection ────────────────────────────────────────────────────

class TestDesignDetection:
    def test_bcra3_2_schools_within_districts(self):
        """TODO example: schools assigned within districts → BCRA3_2."""
        desc = (
            "We are randomly assigning schools within districts to receive "
            "a new math curriculum. Students are nested within schools."
        )
        result = classify_study(desc)
        assert result.design == "BCRA3_2"
        assert result.confidence >= 0.7

    def test_cra3_3_district_randomization(self):
        """Districts randomly assigned → CRA3_3."""
        desc = (
            "Districts are randomly assigned to treatment or control. "
            "Schools and students are nested within districts."
        )
        result = classify_study(desc)
        assert result.design == "CRA3_3"

    def test_cra2_2_classroom_randomization(self):
        """Classrooms randomly assigned, no blocking → CRA2_2."""
        desc = (
            "Classrooms are randomly assigned to the intervention. "
            "Students are nested within classrooms."
        )
        result = classify_study(desc)
        assert result.design == "CRA2_2"

    def test_bcra2_2_classrooms_within_schools(self):
        """Classrooms assigned within schools → BCRA2_2."""
        desc = (
            "Classrooms are randomly assigned within schools. "
            "Students are nested within classrooms."
        )
        result = classify_study(desc)
        assert result.design == "BCRA2_2"

    def test_individual_randomization(self):
        """Individual-level language should map to INDIV_RCT."""
        desc = (
            "Participants are individually randomized to the intervention or control. "
            "No clusters are involved."
        )
        result = classify_study(desc)
        assert result.design == "INDIV_RCT"
        assert result.confidence <= 0.7  # should be moderate without nesting


# ── Confidence scoring rubric ─────────────────────────────────────────────────

class TestConfidenceRubric:
    def test_high_confidence_explicit_assignment_and_nesting(self):
        """Explicit assignment unit + explicit nesting → >= 0.7."""
        desc = (
            "We are randomly assigning schools within districts. "
            "Students are nested within schools."
        )
        result = classify_study(desc)
        assert result.confidence >= 0.7

    def test_moderate_confidence_keywords_only(self):
        """Only keyword mentions without verbs or nesting → lower confidence."""
        desc = "schools classrooms districts"
        result = classify_study(desc)
        assert result.confidence < 0.7

    def test_confidence_capped_at_1(self):
        """Confidence should never exceed 1.0."""
        desc = (
            "We are randomly assigning schools within districts. "
            "Students are nested within schools in a blocked design. "
            "Randomization is stratified by grade."
        )
        result = classify_study(desc)
        assert result.confidence <= 1.0

    def test_confidence_increases_with_nesting_keyword(self):
        """Adding 'nested within' should increase confidence."""
        base_desc = "Randomly assigning classrooms to treatment."
        nested_desc = base_desc + " Students are nested within classrooms."
        r_base = classify_study(base_desc)
        r_nested = classify_study(nested_desc)
        assert r_nested.confidence > r_base.confidence


# ── Rationale output ──────────────────────────────────────────────────────────

class TestRationale:
    def test_rationale_is_non_empty(self):
        desc = (
            "We are randomly assigning schools within districts. "
            "Students are nested within schools."
        )
        result = classify_study(desc)
        assert isinstance(result.rationale, str)
        assert len(result.rationale) > 0

    def test_rationale_mentions_blocking_for_bcra3_2(self):
        desc = (
            "Schools are randomly assigned within districts. "
            "Students are nested within schools."
        )
        result = classify_study(desc)
        if result.design == "BCRA3_2":
            assert "blocking" in result.rationale or "within" in result.rationale.lower()

    def test_rationale_is_string_for_all_designs(self):
        descriptions = [
            "Randomizing districts. Schools nested in districts.",
            "Randomly assigning classrooms. Students nested within classrooms.",
            "Classrooms randomized within schools. Students in classrooms.",
            "Randomly assigning schools within districts.",
        ]
        for desc in descriptions:
            result = classify_study(desc)
            assert isinstance(result.rationale, str)


# ── New keyword coverage ──────────────────────────────────────────────────────

class TestExpandedKeywords:
    def test_section_triggers_l2(self):
        """'section' should be recognized as an L2 cluster unit."""
        desc = "Randomly assigning sections to different teaching methods."
        result = classify_study(desc)
        assert result.design in ("CRA2_2", "BCRA2_2")

    def test_therapist_triggers_l2(self):
        """'therapist' and 'therapists' (plural) should be recognized as L2 clusters."""
        for desc in [
            "Therapists are randomly assigned to deliver the intervention.",
            "A therapist was randomly assigned to each condition.",
        ]:
            result = classify_study(desc)
            assert result.design in ("CRA2_2", "BCRA2_2"), f"Failed for: {desc!r}"

    def test_clinic_triggers_l3(self):
        """'clinic' and 'clinics' (plural) should be recognized as L3 clusters."""
        for desc in [
            "Clinics are randomly assigned to the treatment condition.",
            "A clinic was randomly assigned to receive the intervention.",
        ]:
            result = classify_study(desc)
            assert result.design in ("CRA3_3", "BCRA3_2"), f"Failed for: {desc!r}"

    def test_center_triggers_l3(self):
        """'center' should be recognized as an L3 cluster unit."""
        desc = "Randomly assigning centers to the intervention group."
        result = classify_study(desc)
        assert result.design in ("CRA3_3", "BCRA3_2")

    def test_plural_within_districts_triggers_blocking(self):
        """'within districts' (plural) should trigger the blocking signal."""
        desc = "Schools are randomly assigned within districts."
        result = classify_study(desc)
        assert result.design in ("BCRA3_2", "BCRA2_2")


# ── Individual-randomization penalty ─────────────────────────────────────────

class TestIndividualPenalty:
    def test_individual_assignment_lowers_crt_scores(self):
        """Individual language should route to INDIV_RCT, not CRTs."""
        desc = (
            "Participants are randomly assigned individually to treatment "
            "or control. No clustering."
        )
        result = classify_study(desc)
        assert result.design == "INDIV_RCT"
        assert result.confidence < 0.8

    def test_youth_in_individual_keywords(self):
        """'youth' should contribute to the individual keyword count."""
        desc = "Youth participants are randomly assigned to the intervention."
        result = classify_study(desc)
        assert result.design == "INDIV_RCT"

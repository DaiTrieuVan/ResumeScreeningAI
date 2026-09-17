# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest

from app.services.criteria_service import CriteriaValidationError, validate_scoring_weights
from app.services.scoring_service import calculate_verified_score, calculate_weighted_score, is_evaluation_stale


def test_published_weights_must_total_one():
    with pytest.raises(CriteriaValidationError) as error:
        validate_scoring_weights({"skills": 0.5, "experience": 0.3, "education": 0.15})

    assert error.value.field_errors["scoring_weights"] == "Tổng trọng số phải bằng 100% (hiện tại 95%)."


def test_official_score_uses_published_component_weights():
    score = calculate_weighted_score(
        {"skills": 80, "experience": 70, "education": 90},
        {"skills": 0.5, "experience": 0.3, "education": 0.2},
    )
    assert score == 79.0


def test_result_is_stale_only_when_criteria_versions_differ():
    assert is_evaluation_stale("criteria-v1", "criteria-v2") is True
    assert is_evaluation_stale("criteria-v2", "criteria-v2") is False


def test_verified_score_uses_evidence_and_keeps_unknown_in_upper_bound():
    score = calculate_verified_score(
        [
            {"category": "SKILL", "weight": 0, "result": "MET", "score": 100},
            {"category": "SKILL", "weight": 0, "result": "UNKNOWN", "score": None},
            {"category": "EXPERIENCE", "weight": 0, "result": "MET", "score": 100},
            {"category": "EDUCATION", "weight": 0, "result": "NOT_MET", "score": 0},
        ],
        {"skills": 0.55, "experience": 0.25, "education": 0.2},
    )

    assert score.component_scores == {"skills": 50.0, "experience": 100.0, "education": 0.0}
    assert score.overall_score == 52.5
    assert score.maximum_possible_score == 80.0
    assert score.evidence_coverage == 72.5


def test_unknown_never_adds_to_verified_score():
    score = calculate_verified_score(
        [{"category": "SKILL", "weight": 0, "result": "UNKNOWN", "score": None}],
        {"skills": 1.0},
    )

    assert score.overall_score == 0.0
    assert score.maximum_possible_score == 100.0
    assert score.evidence_coverage == 0.0

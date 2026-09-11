import pytest

from app.services.criteria_service import CriteriaValidationError, validate_scoring_weights
from app.services.scoring_service import calculate_weighted_score, is_evaluation_stale


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

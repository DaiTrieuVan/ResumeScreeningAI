# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import app.models.candidate_evaluation  # noqa: F401
import app.models.candidate_resume  # noqa: F401
import app.models.job_posting  # noqa: F401
import app.models.screening_result  # noqa: F401

from app.models.candidate_resume import CandidateResume
from app.models.screening_criteria import Criterion
from app.services.evidence_service import evaluate_criterion, find_text_evidence


def test_skill_match_returns_source_offsets_and_excerpt():
    resume = CandidateResume(
        file_name="candidate.pdf", file_path="candidate.pdf", file_size_bytes=100,
        raw_text="Backend engineer with production Python and FastAPI experience.",
    )
    criterion = Criterion(
        category="SKILL", importance="MANDATORY", label="Python",
        operator="CONTAINS_ANY", expected_value=["Python"], weight=0, sort_order=0,
    )
    outcome, confidence, _, evidence = evaluate_criterion(criterion, resume)
    assert outcome == "MET"
    assert confidence >= 0.9
    assert resume.raw_text[evidence["start_offset"]:evidence["end_offset"]] == "Python"
    assert "FastAPI" in evidence["excerpt"]


def test_missing_skill_is_unknown_not_false_failure():
    resume = CandidateResume(
        file_name="candidate.pdf", file_path="candidate.pdf", file_size_bytes=100,
        raw_text="Experienced backend engineer.",
    )
    criterion = Criterion(
        category="SKILL", importance="MANDATORY", label="Kubernetes",
        operator="CONTAINS_ANY", expected_value=["Kubernetes"], weight=0, sort_order=0,
    )
    outcome, confidence, explanation, evidence = evaluate_criterion(criterion, resume)
    assert outcome == "UNKNOWN"
    assert confidence < 0.6
    assert evidence is None
    assert "Không tìm thấy bằng chứng" in explanation


def test_evidence_search_is_case_insensitive():
    assert find_text_evidence("PYTHON developer", ["python"])["start_offset"] == 0


def test_composite_contains_any_matches_an_atomic_skill():
    resume = CandidateResume(
        file_name="candidate.pdf", file_path="candidate.pdf", file_size_bytes=100,
        raw_text="Built accessible pages with HTML.",
    )
    criterion = Criterion(
        category="SKILL", importance="MANDATORY", label="HTML/CSS/JavaScript",
        operator="CONTAINS_ANY", expected_value=["HTML/CSS/JavaScript"], weight=0, sort_order=0,
    )

    outcome, _, _, evidence = evaluate_criterion(criterion, resume)

    assert outcome == "MET"
    assert resume.raw_text[evidence["start_offset"]:evidence["end_offset"]] == "HTML"


def test_experience_can_be_verified_from_date_ranges():
    resume = CandidateResume(
        file_name="candidate.pdf", file_path="candidate.pdf", file_size_bytes=100,
        raw_text="Software Engineer 09/2006 to 08/2010 Company Name",
    )
    criterion = Criterion(
        category="EXPERIENCE", importance="MANDATORY", label="Tối thiểu 1 năm kinh nghiệm",
        operator="MIN_VALUE", expected_value=1, weight=0, sort_order=0,
    )

    outcome, confidence, explanation, evidence = evaluate_criterion(criterion, resume)

    assert outcome == "MET"
    assert confidence >= 0.8
    assert "3.9 năm" in explanation
    assert "09/2006 to 08/2010" in evidence["excerpt"]

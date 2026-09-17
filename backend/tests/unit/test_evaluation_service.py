# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest

from app.services.evaluation_service import calculate_metrics, validate_dataset


def _dataset():
    candidates = []
    for job_index in range(3):
        for rank in range(1, 11):
            expected = "UNKNOWN" if rank == 10 else ("PASS" if rank <= 5 else "FAIL")
            candidates.append({
                "id": f"cv-{job_index + 1}-{rank}",
                "job_id": f"job-{job_index + 1}",
                "expert_rank": rank,
                "predicted_score": 101 - rank,
                "criteria": [{
                    "mandatory": True,
                    "expected": expected,
                    "predicted": expected,
                    "evidence": [{"verified": True}] if expected == "PASS" else [],
                }],
                "batch_status": "COMPLETED",
            })
    return {"version": "test-v1", "jobs": [{"id": f"job-{i}"} for i in range(1, 4)], "candidates": candidates}


def test_metrics_include_honest_counts_thresholds_and_status():
    metrics = {item["name"]: item for item in calculate_metrics(_dataset())}

    mandatory = metrics["MANDATORY_RECALL"]
    assert mandatory["numerator"] == 15
    assert mandatory["denominator"] == 15
    assert mandatory["value"] == pytest.approx(1.0)
    assert mandatory["threshold"] == pytest.approx(0.9)
    assert mandatory["status"] == "PASSED"
    assert metrics["EVIDENCE_PRECISION"]["value"] == 1.0
    assert metrics["UNKNOWN_ACCURACY"]["denominator"] == 3
    assert metrics["RANKING_AGREEMENT"]["denominator"] == 135
    assert metrics["BATCH_COMPLETION"]["value"] == 1.0


def test_dataset_rejects_too_few_jobs_or_candidates():
    with pytest.raises(ValueError, match="30"):
        validate_dataset({
            "version": "bad",
            "jobs": [{"id": "one"}, {"id": "two"}, {"id": "three"}],
            "candidates": [],
        })


def test_zero_denominator_is_not_computable_instead_of_being_invented():
    dataset = _dataset()
    for candidate in dataset["candidates"]:
        candidate["criteria"] = []
    metrics = {item["name"]: item for item in calculate_metrics(dataset)}
    assert metrics["MANDATORY_RECALL"]["status"] == "NOT_COMPUTABLE"
    assert metrics["MANDATORY_RECALL"]["value"] is None

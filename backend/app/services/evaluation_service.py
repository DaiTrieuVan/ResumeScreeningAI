# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.final_release import EvaluationRun, MetricResult
from app.services.evaluation_report_service import build_report, write_report


THRESHOLDS = {
    "MANDATORY_RECALL": 0.90,
    "EVIDENCE_PRECISION": 0.90,
    "UNKNOWN_ACCURACY": 0.95,
    "RANKING_AGREEMENT": 0.70,
    "BATCH_COMPLETION": 1.00,
}
TERMINAL_BATCH_STATUSES = {"COMPLETED", "FAILED", "NEEDS_OCR", "DEDUPE_REVIEW", "CANCELLED"}


def load_dataset(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as source:
        return json.load(source)


def validate_dataset(dataset: dict[str, Any]) -> None:
    if not dataset.get("version"):
        raise ValueError("Dataset phải có version.")
    jobs = dataset.get("jobs", [])
    candidates = dataset.get("candidates", [])
    if len(jobs) < 3:
        raise ValueError("Dataset final phải có ít nhất 3 JD.")
    if len(candidates) < 30:
        raise ValueError("Dataset final phải có ít nhất 30 CV.")
    job_ids = {job.get("id") for job in jobs}
    if None in job_ids or any(candidate.get("job_id") not in job_ids for candidate in candidates):
        raise ValueError("Mọi CV phải tham chiếu một JD hợp lệ.")
    if dataset.get("provenance", {}).get("kind") not in {"SYNTHETIC", "ANONYMIZED"}:
        raise ValueError("Dataset phải khai báo nguồn SYNTHETIC hoặc ANONYMIZED.")


def _metric(name: str, numerator: float, denominator: float) -> dict[str, Any]:
    threshold = THRESHOLDS[name]
    if denominator <= 0:
        return {"name": name, "numerator": numerator, "denominator": denominator, "value": None, "threshold": threshold, "status": "NOT_COMPUTABLE"}
    value = numerator / denominator
    return {"name": name, "numerator": numerator, "denominator": denominator, "value": value, "threshold": threshold, "status": "PASSED" if value >= threshold else "FAILED"}


def calculate_metrics(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = dataset.get("candidates", [])
    criteria = [criterion for candidate in candidates for criterion in candidate.get("criteria", [])]
    expected_positive = [item for item in criteria if item.get("mandatory") and item.get("expected") == "PASS"]
    true_positive = sum(item.get("predicted") == "PASS" for item in expected_positive)

    predicted_evidence = [evidence for item in criteria for evidence in item.get("evidence", [])]
    verified_evidence = sum(evidence.get("verified") is True for evidence in predicted_evidence)

    expected_unknown = [item for item in criteria if item.get("expected") == "UNKNOWN"]
    correct_unknown = sum(item.get("predicted") == "UNKNOWN" for item in expected_unknown)

    concordant = 0
    comparable = 0
    for job in dataset.get("jobs", []):
        ranked = [candidate for candidate in candidates if candidate.get("job_id") == job.get("id")]
        for left_index, left in enumerate(ranked):
            for right in ranked[left_index + 1:]:
                expert_delta = left["expert_rank"] - right["expert_rank"]
                predicted_delta = left["predicted_score"] - right["predicted_score"]
                if expert_delta == 0 or predicted_delta == 0:
                    continue
                comparable += 1
                concordant += (expert_delta < 0 and predicted_delta > 0) or (expert_delta > 0 and predicted_delta < 0)

    completed = sum(candidate.get("batch_status") in TERMINAL_BATCH_STATUSES for candidate in candidates)
    return [
        _metric("MANDATORY_RECALL", true_positive, len(expected_positive)),
        _metric("EVIDENCE_PRECISION", verified_evidence, len(predicted_evidence)),
        _metric("UNKNOWN_ACCURACY", correct_unknown, len(expected_unknown)),
        _metric("RANKING_AGREEMENT", concordant, comparable),
        _metric("BATCH_COMPLETION", completed, len(candidates)),
    ]


async def execute_evaluation_run(
    db: AsyncSession,
    *,
    dataset_path: str | Path,
    artifact_dir: str | Path,
    metadata: dict[str, Any],
) -> EvaluationRun:
    dataset = load_dataset(dataset_path)
    validate_dataset(dataset)
    run = EvaluationRun(
        dataset_id=dataset.get("id", "unknown"),
        dataset_version=dataset["version"],
        release_version=metadata["release_version"],
        commit_sha=metadata["commit_sha"],
        criteria_versions={job["id"]: job.get("criteria_version") for job in dataset["jobs"]},
        model_info=metadata.get("model_metadata", {}),
        prompt_version=metadata.get("prompt_version"),
        fallback_mode=metadata["fallback_mode"],
        status="RUNNING",
        started_at=datetime.utcnow(),
    )
    db.add(run)
    await db.flush()
    metrics = calculate_metrics(dataset)
    for metric in metrics:
        db.add(MetricResult(
            evaluation_run_id=run.id,
            metric_name=metric["name"],
            numerator=metric["numerator"],
            denominator=metric["denominator"],
            value=metric["value"],
            threshold=metric["threshold"],
            status=metric["status"],
        ))
    report = build_report(metadata, dataset, metrics)
    json_path, markdown_path = write_report(report, artifact_dir, f"{dataset['version']}-{run.id}")
    run.report_json_path = str(json_path)
    run.report_md_path = str(markdown_path)
    run.status = report["status"]
    run.completed_at = datetime.utcnow()
    await db.flush()
    return run


async def serialize_evaluation_run(db: AsyncSession, run: EvaluationRun) -> dict[str, Any]:
    results = (await db.execute(select(MetricResult).where(MetricResult.evaluation_run_id == run.id))).scalars().all()
    return {
        "id": run.id,
        "status": run.status,
        "dataset_version": run.dataset_version,
        "release_version": run.release_version,
        "commit_sha": run.commit_sha,
        "fallback_mode": run.fallback_mode,
        "metrics": [{
            "name": item.metric_name,
            "numerator": item.numerator,
            "denominator": item.denominator,
            "value": item.value,
            "threshold": item.threshold,
            "status": item.status,
        } for item in results],
        "report_urls": {"json": run.report_json_path, "markdown": run.report_md_path},
    }


# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_report(metadata: dict[str, Any], dataset: dict[str, Any], metrics: list[dict[str, Any]]) -> dict[str, Any]:
    status = "PASSED" if metrics and all(metric["status"] == "PASSED" for metric in metrics) else "FAILED"
    return {
        "schema_version": "1.0.0",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "release": {"version": metadata["release_version"], "commit_sha": metadata["commit_sha"]},
        "dataset": {
            "id": dataset.get("id"),
            "version": dataset["version"],
            "sample_count": len(dataset.get("candidates", [])),
            "job_count": len(dataset.get("jobs", [])),
            "label_schema_version": dataset.get("label_schema_version"),
            "provenance": dataset.get("provenance"),
        },
        "configuration": {
            "criteria_versions": {job["id"]: job.get("criteria_version") for job in dataset.get("jobs", [])},
            "fallback_mode": metadata["fallback_mode"],
            "model": metadata.get("model_metadata", {}),
            "prompt_version": metadata.get("prompt_version"),
        },
        "metrics": metrics,
        "limitations": [
            "Synthetic deterministic baseline; it validates repeatability and metric plumbing, not production accuracy.",
            "External-validity testing with independently labeled anonymized CVs remains a future production gate.",
        ],
    }


def write_report(report: dict[str, Any], output_dir: str | Path, stem: str) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / f"{stem}.json"
    markdown_path = output / f"{stem}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = [
        "# AI evaluation report",
        "",
        f"**Status:** {report['status']}",
        f"**Release:** {report['release']['version']} (`{report['release']['commit_sha']}`)",
        f"**Dataset:** {report['dataset']['id']} / {report['dataset']['version']} — {report['dataset']['sample_count']} CV, {report['dataset']['job_count']} JD",
        f"**Mode:** {'offline fallback' if report['configuration']['fallback_mode'] else 'configured AI'}",
        f"**Measured at:** {report['measured_at']}",
        "",
        "| Metric | Numerator | Denominator | Value | Threshold | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for metric in report["metrics"]:
        value = "N/A" if metric["value"] is None else f"{metric['value']:.4f}"
        rows.append(f"| {metric['name']} | {metric['numerator']} | {metric['denominator']} | {value} | {metric['threshold']:.2f} | {metric['status']} |")
    rows.extend(["", "## Limitations", "", *[f"- {item}" for item in report["limitations"]], ""])
    markdown_path.write_text("\n".join(rows), encoding="utf-8")
    return json_path, markdown_path

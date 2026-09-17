# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.evaluation_report_service import build_report, write_report  # noqa: E402
from app.services.evaluation_service import calculate_metrics, load_dataset, validate_dataset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic Resume Screening AI benchmark.")
    parser.add_argument("--dataset", default="competition-v1")
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--model", default="deterministic-offline-v1")
    parser.add_argument("--prompt-version", default="criteria-evidence-v1")
    parser.add_argument("--online", action="store_true", help="Record configured-AI mode instead of offline fallback.")
    parser.add_argument("--output-dir", default=str(ROOT / "artifacts" / "benchmark"))
    args = parser.parse_args()

    dataset_path = ROOT / "evaluation" / "datasets" / args.dataset / "manifest.json"
    dataset = load_dataset(dataset_path)
    validate_dataset(dataset)
    metrics = calculate_metrics(dataset)
    report = build_report({
        "release_version": args.release_version,
        "commit_sha": args.commit_sha,
        "fallback_mode": not args.online,
        "model_metadata": {"name": args.model},
        "prompt_version": args.prompt_version,
    }, dataset, metrics)
    json_path, markdown_path = write_report(report, args.output_dir, args.dataset)
    print(json.dumps({"status": report["status"], "json": str(json_path), "markdown": str(markdown_path)}, ensure_ascii=False))
    return 0 if report["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

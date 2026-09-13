# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from pathlib import Path

from app.services.evaluation_service import load_dataset, validate_dataset


def test_competition_dataset_meets_minimum_coverage():
    root = Path(__file__).resolve().parents[3]
    dataset = load_dataset(root / "evaluation" / "datasets" / "competition-v1" / "manifest.json")
    validate_dataset(dataset)
    assert len(dataset["jobs"]) >= 3
    assert len(dataset["candidates"]) >= 30
    assert dataset["provenance"]["kind"] == "SYNTHETIC"


# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from dataclasses import dataclass


SCORING_VERSION = "criterion-evidence-v2"

CATEGORY_COMPONENTS = {
    "SKILL": "skills",
    "EXPERIENCE": "experience",
    "EDUCATION": "education",
}


@dataclass(frozen=True)
class VerifiedScore:
    component_scores: dict[str, float]
    overall_score: float
    maximum_possible_score: float
    evidence_coverage: float


def _criterion_bounds(result: str, score: float | None = None) -> tuple[float, float, bool]:
    """Return conservative lower/upper match bounds and whether evidence is known."""

    if result == "MET":
        return 1.0, 1.0, True
    if result == "PARTIAL":
        value = max(0.0, min(1.0, (score if score is not None else 50.0) / 100.0))
        return value, value, True
    if result == "NOT_MET":
        return 0.0, 0.0, True
    if result in {"NOT_APPLICABLE", "N/A"}:
        return 0.0, 0.0, False
    return 0.0, 1.0, False


def calculate_verified_score(
    criterion_results: list[dict], scoring_weights: dict[str, float]
) -> VerifiedScore:
    """Calculate an evidence-backed score; UNKNOWN can raise only the upper bound."""

    grouped: dict[str, list[dict]] = {key: [] for key in scoring_weights}
    for item in criterion_results:
        category = str(item.get("category", "")).upper()
        component = CATEGORY_COMPONENTS.get(category, category.lower())
        if component in grouped and item.get("result") not in {"NOT_APPLICABLE", "N/A"}:
            grouped[component].append(item)

    total_component_weight = sum(max(0.0, value) for value in scoring_weights.values()) or 1.0
    component_scores: dict[str, float] = {}
    overall_lower = 0.0
    overall_upper = 0.0
    coverage = 0.0

    for component, configured_weight in scoring_weights.items():
        component_weight = max(0.0, configured_weight) / total_component_weight
        items = grouped.get(component, [])
        if not items:
            component_scores[component] = 0.0
            overall_upper += component_weight * 100.0
            continue

        positive_weights = [max(0.0, float(item.get("weight") or 0.0)) for item in items]
        if sum(positive_weights) <= 0:
            item_weights = [1.0 / len(items)] * len(items)
        else:
            weight_total = sum(positive_weights)
            item_weights = [value / weight_total for value in positive_weights]

        component_lower = 0.0
        component_upper = 0.0
        component_coverage = 0.0
        for item, item_weight in zip(items, item_weights):
            lower, upper, known = _criterion_bounds(str(item.get("result", "UNKNOWN")), item.get("score"))
            component_lower += item_weight * lower
            component_upper += item_weight * upper
            if known:
                component_coverage += item_weight

        component_scores[component] = round(component_lower * 100.0, 1)
        overall_lower += component_weight * component_lower * 100.0
        overall_upper += component_weight * component_upper * 100.0
        coverage += component_weight * component_coverage * 100.0

    return VerifiedScore(
        component_scores=component_scores,
        overall_score=round(overall_lower, 1),
        maximum_possible_score=round(overall_upper, 1),
        evidence_coverage=round(coverage, 1),
    )

def calculate_weighted_score(
    component_scores: dict[str, float], scoring_weights: dict[str, float]
) -> float:
    return round(
        sum(component_scores.get(key, 0.0) * weight for key, weight in scoring_weights.items()),
        1,
    )


def is_evaluation_stale(
    evaluation_criteria_set_id: str | None, active_criteria_set_id: str | None
) -> bool:
    return bool(
        evaluation_criteria_set_id
        and active_criteria_set_id
        and evaluation_criteria_set_id != active_criteria_set_id
    )

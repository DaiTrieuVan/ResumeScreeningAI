# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

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

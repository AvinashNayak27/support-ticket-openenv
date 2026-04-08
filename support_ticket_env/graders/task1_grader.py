"""
Task 1 Grader -- Ticket Classification (Easy)
Scores 0.0-1.0 based on category + priority accuracy.
"""
from __future__ import annotations
from typing import Dict, Any, Tuple

VALID_CATEGORIES = {"billing", "technical", "account", "shipping", "general"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}

PRIORITY_DISTANCE = {
    "low": 0, "medium": 1, "high": 2, "critical": 3
}


def grade_task1(action: Dict[str, Any], ground_truth: Dict[str, Any]) -> Tuple[float, Dict[str, float], str]:
    """
    Returns (total_reward, score_breakdown, feedback_message).

    Scoring:
    - Category exact match: 0.5 points
    - Priority exact match: 0.5 points
      - Off by 1 level: 0.25 points
      - Off by 2+ levels: 0.0 points
    """
    scores: Dict[str, float] = {}
    feedback_parts = []

    predicted_cat = (action.get("category") or "").strip().lower()
    true_cat = ground_truth["category"].lower()

    if predicted_cat == true_cat:
        scores["category"] = 0.5
        feedback_parts.append(f"Category '{predicted_cat}' is correct. (+0.5)")
    elif predicted_cat in VALID_CATEGORIES:
        scores["category"] = 0.0
        feedback_parts.append(f"Category '{predicted_cat}' is wrong (expected '{true_cat}'). (+0.0)")
    else:
        scores["category"] = 0.0
        feedback_parts.append(f"Category '{predicted_cat}' is invalid. Must be one of {sorted(VALID_CATEGORIES)}. (+0.0)")

    predicted_pri = (action.get("priority") or "").strip().lower()
    true_pri = ground_truth["priority"].lower()

    if predicted_pri == true_pri:
        scores["priority"] = 0.5
        feedback_parts.append(f"Priority '{predicted_pri}' is correct. (+0.5)")
    elif predicted_pri in VALID_PRIORITIES:
        dist = abs(PRIORITY_DISTANCE[predicted_pri] - PRIORITY_DISTANCE[true_pri])
        if dist == 1:
            scores["priority"] = 0.25
            feedback_parts.append(
                f"Priority '{predicted_pri}' is off by 1 level (expected '{true_pri}'). (+0.25)"
            )
        else:
            scores["priority"] = 0.0
            feedback_parts.append(
                f"Priority '{predicted_pri}' is too far off (expected '{true_pri}'). (+0.0)"
            )
    else:
        scores["priority"] = 0.0
        feedback_parts.append(f"Priority '{predicted_pri}' is invalid. Must be one of {sorted(VALID_PRIORITIES)}. (+0.0)")

    total = sum(scores.values())
    feedback = " | ".join(feedback_parts)
    return round(total, 4), scores, feedback

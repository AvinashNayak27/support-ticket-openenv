"""
Task 3 Grader -- Full Resolution Pipeline (Hard)
Scores strictly between 0 and 1 combining classification + response + resolution.
"""
from __future__ import annotations
from typing import Dict, Any, Tuple
from .task1_grader import grade_task1
from .task2_grader import grade_task2
import re

STOP_WORDS = {
    "the", "a", "an", "and", "or", "in", "on", "at", "to", "for",
    "is", "are", "was", "were", "be", "been", "if", "of", "with",
    "that", "this", "it", "by", "from", "not", "have", "has"
}


def grade_task3(action: Dict[str, Any], ground_truth: Dict[str, Any], ticket: Dict[str, Any]) -> Tuple[float, Dict[str, float], str]:
    """
    Returns (total_reward, score_breakdown, feedback_message).

    Scoring breakdown (total = 1.0):
    - Classification (0.2): category + priority (scaled from task1)
    - Response quality (0.3): scaled from task2
    - Resolution steps coverage (0.3): fraction of expected steps addressed
    - Resolution correctness (0.2): resolved=True + summary quality
    """
    scores: Dict[str, float] = {}
    feedback_parts = []

    t1_score, t1_breakdown, t1_fb = grade_task1(action, ground_truth)
    clf_score = round(t1_score * 0.2, 4)
    scores["classification"] = clf_score
    feedback_parts.append(f"Classification: {t1_fb} => scaled to +{clf_score:.2f}")

    t2_score, t2_breakdown, t2_fb = grade_task2(action, ground_truth, ticket)
    resp_score = round(t2_score * 0.3, 4)
    scores["response_quality"] = resp_score
    feedback_parts.append(f"Response: {t2_fb} => scaled to +{resp_score:.2f}")

    expected_steps = ground_truth.get("resolution_steps", [])
    agent_steps = action.get("resolution_steps") or []
    agent_steps_text = " ".join(str(s).lower() for s in agent_steps)

    if expected_steps and agent_steps:
        step_scores = []
        for exp_step in expected_steps:
            exp_words = set(re.findall(r'\w+', exp_step.lower())) - STOP_WORDS
            if exp_words:
                overlap = sum(1 for w in exp_words if w in agent_steps_text)
                step_scores.append(overlap / len(exp_words))
            else:
                step_scores.append(0.0)
        steps_coverage = sum(step_scores) / len(step_scores)
        steps_score = round(steps_coverage * 0.3, 4)
        feedback_parts.append(f"Resolution steps coverage: {steps_coverage:.0%} (+{steps_score:.2f})")
    elif not agent_steps:
        steps_score = 0.0
        feedback_parts.append("No resolution_steps provided. (+0.00)")
    else:
        steps_score = 0.15
        feedback_parts.append(f"Steps provided but no reference. Partial credit. (+{steps_score:.2f})")

    scores["resolution_steps"] = steps_score

    res_score = 0.0
    resolved = action.get("resolved")
    summary = (action.get("resolution_summary") or "").strip()

    if resolved is True:
        res_score += 0.1
        feedback_parts.append("resolved=True (+0.10)")
    else:
        feedback_parts.append("resolved not set to True (+0.00)")

    if summary and len(summary.split()) >= 10:
        res_score += 0.1
        feedback_parts.append(f"Summary provided ({len(summary.split())} words) (+0.10)")
    else:
        feedback_parts.append(f"Summary missing or too short (+0.00)")

    scores["resolution_correctness"] = round(res_score, 4)

    total = sum(scores.values())
    total = max(0.01, min(0.99, total))
    feedback = " | ".join(feedback_parts)
    return round(total, 4), scores, feedback

"""
Task 2 Grader -- Response Drafting (Medium)
Scores 0.0-1.0 based on response quality.
"""
from __future__ import annotations
from typing import Dict, Any, Tuple
import re


def grade_task2(action: Dict[str, Any], ground_truth: Dict[str, Any], ticket: Dict[str, Any]) -> Tuple[float, Dict[str, float], str]:
    """
    Returns (total_reward, score_breakdown, feedback_message).

    Scoring breakdown (total = 1.0):
    - Keyword coverage (0.4): fraction of expected keywords present
    - Personalization (0.2): uses customer name
    - Professionalism (0.2): polite opener/closer present
    - Length appropriateness (0.2): 50-500 words
    """
    scores: Dict[str, float] = {}
    feedback_parts = []

    response = (action.get("response_draft") or "").strip()
    response_lower = response.lower()

    if not response:
        return 0.0, {"keyword_coverage": 0.0, "personalization": 0.0, "professionalism": 0.0, "length": 0.0}, "No response_draft provided."

    keywords = ground_truth.get("response_keywords", [])
    if keywords:
        matched = sum(1 for kw in keywords if kw.lower() in response_lower)
        kw_score = (matched / len(keywords)) * 0.4
    else:
        kw_score = 0.4
    scores["keyword_coverage"] = round(kw_score, 4)
    feedback_parts.append(f"Keywords matched {int(kw_score/0.4*len(keywords)) if keywords else 'N/A'}/{len(keywords)} (+{kw_score:.2f})")

    customer_name = ticket.get("customer_name", "")
    first_name = customer_name.split()[0] if customer_name else ""
    if first_name and first_name.lower() in response_lower:
        scores["personalization"] = 0.2
        feedback_parts.append("Response addresses customer by name. (+0.20)")
    else:
        scores["personalization"] = 0.0
        feedback_parts.append(f"Response doesn't address customer ('{first_name}'). (+0.00)")

    polite_openers = ["dear", "hello", "hi ", "thank you", "thanks for"]
    polite_closers = ["sincerely", "regards", "best", "thank you", "let us know", "please don't hesitate"]
    has_opener = any(op in response_lower for op in polite_openers)
    has_closer = any(cl in response_lower for cl in polite_closers)
    prof_score = 0.0
    if has_opener:
        prof_score += 0.1
    if has_closer:
        prof_score += 0.1
    scores["professionalism"] = round(prof_score, 4)
    feedback_parts.append(
        f"Professionalism: opener={'yes' if has_opener else 'no'}, closer={'yes' if has_closer else 'no'}. (+{prof_score:.2f})"
    )

    word_count = len(response.split())
    if 50 <= word_count <= 500:
        scores["length"] = 0.2
        feedback_parts.append(f"Length OK ({word_count} words). (+0.20)")
    elif word_count < 50:
        scores["length"] = round((word_count / 50) * 0.2, 4)
        feedback_parts.append(f"Response too short ({word_count} words, need 50+). (+{scores['length']:.2f})")
    else:
        scores["length"] = 0.1
        feedback_parts.append(f"Response too long ({word_count} words, max 500). (+0.10)")

    total = sum(scores.values())
    feedback = " | ".join(feedback_parts)
    return round(total, 4), scores, feedback

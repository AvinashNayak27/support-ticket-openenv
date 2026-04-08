#!/usr/bin/env python3
"""
inference.py - Inference script for Support Ticket OpenEnv environment.

STDOUT FORMAT (required by validator):
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Dict, Any, List, Optional

import httpx
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
HF_TOKEN: str = os.environ.get("HF_TOKEN") or os.environ.get("OPENAI_API_KEY", "")
ENV_BASE_URL: str = os.environ.get("ENV_BASE_URL", "https://avinashnayak-support-ticket-openenv.hf.space")
NUM_EPISODES: int = int(os.environ.get("NUM_EPISODES", "5"))
BENCHMARK: str = "support-ticket"

if not HF_TOKEN:
    print("[ERROR] Set HF_TOKEN or OPENAI_API_KEY environment variable.", file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)


# ---------------------------------------------------------------------------
# Structured stdout logging helpers
# ---------------------------------------------------------------------------
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    done_val = str(done).lower()
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Environment HTTP helpers
# ---------------------------------------------------------------------------
def env_reset(task_id: str, seed: int) -> dict:
    resp = httpx.post(
        f"{ENV_BASE_URL}/reset",
        json={"task_id": task_id, "seed": seed},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_step(action: dict) -> dict:
    resp = httpx.post(
        f"{ENV_BASE_URL}/step",
        json={"action": action},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Task-specific system prompts
# ---------------------------------------------------------------------------
TASK_SYSTEM_PROMPTS = {
    "task_1_classify": (
        "You are a customer support triage specialist. "
        "Given a support ticket, classify it with:\n"
        "  - category: one of [billing, technical, account, shipping, general]\n"
        "  - priority: one of [low, medium, high, critical]\n\n"
        'Respond ONLY with a JSON object: {"category": "<value>", "priority": "<value>"}'
    ),
    "task_2_respond": (
        "You are a professional customer support agent. "
        "Draft a helpful, empathetic response to the customer ticket. "
        "Address the customer by first name. Include polite opener and closer. 50-500 words.\n\n"
        'Respond ONLY with: {"response_draft": "<your response here>"}'
    ),
    "task_3_resolve": (
        "You are a senior customer support engineer. Provide a complete resolution:\n"
        "  1. category, 2. priority, 3. response_draft (50-500 words),\n"
        "  4. resolution_steps (ordered list), 5. resolved: true,\n"
        "  6. resolution_summary (1-2 sentences)\n\n"
        'Respond ONLY with JSON: {"category":"...","priority":"...","response_draft":"...",'
        '"resolution_steps":[...],"resolved":true,"resolution_summary":"..."}'
    ),
}


def build_user_prompt(obs: dict) -> str:
    o = obs["observation"]
    return (
        f"Ticket ID: {o['ticket_id']}\n"
        f"Customer: {o['customer_name']} ({o['customer_tier']} tier)\n"
        f"Subject: {o['ticket_subject']}\n"
        f"Message:\n{o['ticket_body']}"
    )


def call_llm(task_id: str, user_prompt: str) -> dict:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": TASK_SYSTEM_PROMPTS[task_id]},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        if not text:
            return {}
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", file=sys.stderr, flush=True)
        return {}


# ---------------------------------------------------------------------------
# Single episode runner
# ---------------------------------------------------------------------------
def run_episode(task_id: str, seed: int) -> float:
    """Run one episode for *task_id* and emit [START]/[STEP]/[END] to stdout.

    Returns the episode score in [0, 1].
    """
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    last_error: Optional[str] = None

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset_resp = env_reset(task_id=task_id, seed=seed)
        obs = reset_resp

        action_payload = call_llm(task_id, build_user_prompt(obs))
        if not action_payload:
            last_error = "LLM returned empty or unparseable response"

        action_payload["ticket_id"] = obs["observation"]["ticket_id"]

        step_resp = env_step(action_payload)
        reward = step_resp.get("reward", 0.0)
        done = step_resp.get("done", False)
        steps_taken = 1
        rewards.append(reward)

        action_summary = _summarize_action(task_id, action_payload)
        log_step(step=1, action=action_summary, reward=reward, done=done, error=last_error)

        score = reward
        score = min(max(score, 0.0), 1.0)
        success = score > 0.0

    except Exception as exc:
        last_error = str(exc)
        print(f"[ERROR] Episode failed: {exc}", file=sys.stderr, flush=True)
        if steps_taken == 0:
            log_step(step=1, action="error", reward=0.0, done=True, error=last_error)
            steps_taken = 1
            rewards.append(0.0)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


def _summarize_action(task_id: str, action: Dict[str, Any]) -> str:
    """Produce a short single-line action string for the [STEP] log."""
    if task_id == "task_1_classify":
        return f"classify({action.get('category','?')},{action.get('priority','?')})"
    if task_id == "task_2_respond":
        draft = (action.get("response_draft") or "")[:40].replace("\n", " ")
        return f"respond('{draft}...')"
    draft = (action.get("response_draft") or "")[:30].replace("\n", " ")
    return f"resolve({action.get('category','?')},{action.get('priority','?')},'{draft}...')"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    tasks = ["task_1_classify", "task_2_respond", "task_3_resolve"]

    print(f"[INFO] Model={MODEL_NAME}, ENV={ENV_BASE_URL}, Episodes/task={NUM_EPISODES}", file=sys.stderr, flush=True)

    for task_id in tasks:
        for ep in range(NUM_EPISODES):
            seed = 42 + ep
            try:
                run_episode(task_id=task_id, seed=seed)
            except Exception as e:
                print(f"[ERROR] Unhandled error in {task_id} ep {ep+1}: {e}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()

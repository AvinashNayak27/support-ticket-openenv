#!/usr/bin/env python3
"""
inference.py - Baseline inference script for Support Ticket OpenEnv environment.

Usage:
    export API_BASE_URL="https://api.openai.com/v1"
    export MODEL_NAME="gpt-4o-mini"
    export HF_TOKEN="hf_..."
    python inference.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
import httpx
from openai import OpenAI

API_BASE_URL: str = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME: str = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN: str = os.environ.get("HF_TOKEN") or os.environ.get("OPENAI_API_KEY", "")
ENV_BASE_URL: str = os.environ.get("ENV_BASE_URL", "http://localhost:7860")
NUM_EPISODES: int = int(os.environ.get("NUM_EPISODES", "5"))

if not HF_TOKEN:
    print("[ERROR] Set HF_TOKEN or OPENAI_API_KEY environment variable.", file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)


def env_reset(task_id: str, seed: int) -> dict:
    resp = httpx.post(f"{ENV_BASE_URL}/reset", json={"task_id": task_id, "seed": seed}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def env_step(action: dict) -> dict:
    resp = httpx.post(f"{ENV_BASE_URL}/step", json={"action": action}, timeout=30)
    resp.raise_for_status()
    return resp.json()


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
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": TASK_SYSTEM_PROMPTS[task_id]},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=1024,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def run_episode(task_id: str, seed: int, episode_num: int) -> dict:
    run_id = str(uuid.uuid4())[:8]
    reset_resp = env_reset(task_id=task_id, seed=seed)
    obs = reset_resp

    print(json.dumps({"type": "START", "run_id": run_id, "task_id": task_id,
                      "episode": episode_num, "seed": seed,
                      "ticket_id": obs["observation"]["ticket_id"],
                      "model": MODEL_NAME, "timestamp": time.time()}), flush=True)

    try:
        action_payload = call_llm(task_id, build_user_prompt(obs))
    except Exception as e:
        action_payload = {}
        print(f"[WARN] LLM parse error: {e}", file=sys.stderr, flush=True)

    action_payload["ticket_id"] = obs["observation"]["ticket_id"]
    step_resp = env_step(action_payload)
    reward = step_resp.get("reward", 0.0)
    scores = step_resp["observation"].get("scores", {})
    feedback = step_resp["observation"].get("feedback", "")
    done = step_resp.get("done", False)

    print(json.dumps({"type": "STEP", "run_id": run_id, "task_id": task_id,
                      "episode": episode_num, "step": 1, "action": action_payload,
                      "reward": reward, "done": done, "scores": scores,
                      "feedback": feedback, "timestamp": time.time()}), flush=True)

    print(json.dumps({"type": "END", "run_id": run_id, "task_id": task_id,
                      "episode": episode_num, "total_reward": reward,
                      "scores": scores, "done": done, "timestamp": time.time()}), flush=True)

    return {"task_id": task_id, "episode": episode_num, "seed": seed, "reward": reward, "scores": scores}


def main():
    tasks = ["task_1_classify", "task_2_respond", "task_3_resolve"]
    all_results = []

    print(f"[INFO] Model={MODEL_NAME}, ENV={ENV_BASE_URL}, Episodes/task={NUM_EPISODES}", file=sys.stderr)

    for task_id in tasks:
        task_rewards = []
        for ep in range(NUM_EPISODES):
            seed = 42 + ep
            try:
                result = run_episode(task_id=task_id, seed=seed, episode_num=ep + 1)
                all_results.append(result)
                task_rewards.append(result["reward"])
            except Exception as e:
                print(f"[ERROR] Episode {ep+1} task {task_id} failed: {e}", file=sys.stderr)
                task_rewards.append(0.0)

        avg = sum(task_rewards) / len(task_rewards) if task_rewards else 0.0
        print(f"[INFO] {task_id}: avg_reward={avg:.4f}", file=sys.stderr)

    overall_avg = sum(r["reward"] for r in all_results) / len(all_results) if all_results else 0.0
    print(json.dumps({"type": "SUMMARY", "model": MODEL_NAME,
                      "total_episodes": len(all_results),
                      "overall_avg_reward": round(overall_avg, 4),
                      "timestamp": time.time()}), flush=True)


if __name__ == "__main__":
    main()

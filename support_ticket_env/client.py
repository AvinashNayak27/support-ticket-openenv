"""
SupportTicketEnv - lightweight HTTP client wrapping the OpenEnv server.
Use this in inference.py or any external agent to interact with the environment.
"""
from __future__ import annotations

import os
from typing import Optional, Dict, Any

import httpx

from .models import TicketAction, TicketObservation, TicketState


DEFAULT_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")


class SupportTicketEnv:
    """
    HTTP client for the Support Ticket OpenEnv server.

    Usage:
        env = SupportTicketEnv(base_url="http://localhost:7860")
        obs = env.reset(task_id="task_1_classify", seed=42)
        action = TicketAction(ticket_id=obs.ticket_id, category="billing", priority="high")
        result = env.step(action)
        print(result.reward, result.feedback)
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def health(self) -> Dict[str, Any]:
        resp = self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    def reset(
        self,
        task_id: str = "task_1_classify",
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
    ) -> TicketObservation:
        payload = {"task_id": task_id}
        if seed is not None:
            payload["seed"] = seed
        if episode_id is not None:
            payload["episode_id"] = episode_id
        resp = self._client.post("/reset", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return TicketObservation(**data["observation"])

    def step(self, action: TicketAction) -> TicketObservation:
        payload = {"action": action.model_dump()}
        resp = self._client.post("/step", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return TicketObservation(**data["observation"])

    def state(self) -> TicketState:
        resp = self._client.get("/state")
        resp.raise_for_status()
        return TicketState(**resp.json())

    def schema(self) -> Dict[str, Any]:
        resp = self._client.get("/schema")
        resp.raise_for_status()
        return resp.json()

    def tasks(self) -> Dict[str, Any]:
        resp = self._client.get("/tasks")
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

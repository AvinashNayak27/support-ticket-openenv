"""
FastAPI application entry point for the Support Ticket OpenEnv environment.
Exposes /reset, /step, /state, /health, /schema endpoints.
Compliant with the OpenEnv HTTP spec.
"""
from __future__ import annotations

import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from ..models import TicketAction, TicketObservation, TicketState
from .environment import SupportTicketEnvironment

app = FastAPI(
    title="Support Ticket OpenEnv",
    description="Customer Support Ticket Management environment for AI agent training.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_env = SupportTicketEnvironment()


class ResetRequest(BaseModel):
    seed: Optional[int] = None
    episode_id: Optional[str] = None
    task_id: Optional[str] = "task_1_classify"


class StepRequest(BaseModel):
    action: TicketAction


class ResetResponse(BaseModel):
    observation: TicketObservation
    reward: Optional[float] = None
    done: bool = False


class StepResponse(BaseModel):
    observation: TicketObservation
    reward: float
    done: bool


@app.get("/health")
def health():
    return {"status": "ok", "env": "support-ticket-env", "version": "1.0.0"}


@app.post("/reset", response_model=ResetResponse)
def reset(req: ResetRequest = ResetRequest()):
    obs = _env.reset(seed=req.seed, episode_id=req.episode_id, task_id=req.task_id)
    return ResetResponse(observation=obs, reward=None, done=False)


@app.post("/step", response_model=StepResponse)
def step(req: StepRequest):
    obs = _env.step(req.action)
    return StepResponse(observation=obs, reward=obs.reward, done=obs.done)


@app.get("/state", response_model=TicketState)
def state():
    return _env.state()


@app.get("/schema")
def schema():
    return {
        "action": TicketAction.model_json_schema(),
        "observation": TicketObservation.model_json_schema(),
        "state": TicketState.model_json_schema(),
    }


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "id": "task_1_classify",
                "name": "Ticket Classification",
                "difficulty": "easy",
                "description": "Classify the ticket by category and priority.",
                "required_action_fields": ["ticket_id", "category", "priority"],
                "max_score": 1.0,
            },
            {
                "id": "task_2_respond",
                "name": "Response Drafting",
                "difficulty": "medium",
                "description": "Draft a professional response to the customer.",
                "required_action_fields": ["ticket_id", "response_draft"],
                "max_score": 1.0,
            },
            {
                "id": "task_3_resolve",
                "name": "Full Resolution Pipeline",
                "difficulty": "hard",
                "description": "Classify, respond, and provide a full resolution plan.",
                "required_action_fields": [
                    "ticket_id", "category", "priority",
                    "response_draft", "resolution_steps",
                    "resolved", "resolution_summary"
                ],
                "max_score": 1.0,
            },
        ]
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

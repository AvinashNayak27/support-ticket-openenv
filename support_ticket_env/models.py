from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid


class TicketAction(BaseModel):
    """Action submitted by the agent to handle a support ticket."""

    ticket_id: str = Field(..., description="ID of the ticket being acted on")

    category: Optional[str] = Field(
        None,
        description="Ticket category: billing | technical | account | shipping | general"
    )
    priority: Optional[str] = Field(
        None,
        description="Priority level: low | medium | high | critical"
    )

    response_draft: Optional[str] = Field(
        None,
        description="Draft response to send to the customer"
    )

    resolution_steps: Optional[List[str]] = Field(
        None,
        description="Ordered list of resolution steps taken"
    )
    resolved: Optional[bool] = Field(
        None,
        description="Whether the ticket is marked as resolved"
    )
    resolution_summary: Optional[str] = Field(
        None,
        description="Brief summary of how the ticket was resolved"
    )


class TicketObservation(BaseModel):
    """Observation returned by the environment after each step."""

    ticket_id: str
    ticket_subject: str
    ticket_body: str
    customer_name: str
    customer_tier: str
    created_at: str

    feedback: str = Field("", description="Environment feedback on the last action")
    reward: float = Field(0.0, description="Reward signal for this step (0.0-1.0)")
    done: bool = Field(False, description="Whether the episode is complete")
    step_count: int = Field(0)

    scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Breakdown of partial scores e.g. {'category': 0.5, 'priority': 0.3}"
    )

    metadata: Dict[str, Any] = Field(default_factory=dict)


class TicketState(BaseModel):
    """Internal episode state."""

    episode_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_count: int = 0
    task_id: str = "task_1_classify"
    current_ticket_id: str = ""
    cumulative_reward: float = 0.0
    is_done: bool = False

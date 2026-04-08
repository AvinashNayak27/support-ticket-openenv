"""
SupportTicketEnvironment -- core environment logic.
Implements OpenEnv's reset() / step() / state() interface.
"""
from __future__ import annotations

import uuid
import random
from typing import Optional

from ..models import TicketAction, TicketObservation, TicketState
from ..data.tickets import TICKETS, TICKET_INDEX
from ..graders import grade_task1, grade_task2, grade_task3


TASK_IDS = ["task_1_classify", "task_2_respond", "task_3_resolve"]
MAX_STEPS_PER_TASK = 1


class SupportTicketEnvironment:
    """
    OpenEnv-compatible environment for Customer Support Ticket Management.

    Three task modes (set via reset(task_id=...)):
      - task_1_classify : Agent must classify category + priority
      - task_2_respond  : Agent must draft a customer response
      - task_3_resolve  : Agent must classify + respond + provide resolution steps
    """

    def __init__(self, task_id: str = "task_1_classify", seed: Optional[int] = None):
        self._task_id = task_id
        self._seed = seed
        self._state = TicketState()
        self._current_ticket: dict = {}
        self._rng = random.Random(seed)

    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, task_id: Optional[str] = None) -> TicketObservation:
        if seed is not None:
            self._rng = random.Random(seed)
            self._seed = seed

        if task_id is not None and task_id in TASK_IDS:
            self._task_id = task_id

        eid = episode_id or str(uuid.uuid4())
        ticket = self._rng.choice(TICKETS)
        self._current_ticket = ticket

        self._state = TicketState(
            episode_id=eid,
            step_count=0,
            task_id=self._task_id,
            current_ticket_id=ticket["ticket_id"],
            cumulative_reward=0.0,
            is_done=False,
        )

        return TicketObservation(
            ticket_id=ticket["ticket_id"],
            ticket_subject=ticket["subject"],
            ticket_body=ticket["body"],
            customer_name=ticket["customer_name"],
            customer_tier=ticket["customer_tier"],
            created_at=ticket["created_at"],
            feedback=f"New episode started. Task: {self._task_id}. Ticket {ticket['ticket_id']} assigned.",
            reward=0.0,
            done=False,
            step_count=0,
            scores={},
            metadata={
                "task_id": self._task_id,
                "episode_id": eid,
                "available_categories": ["billing", "technical", "account", "shipping", "general"],
                "available_priorities": ["low", "medium", "high", "critical"],
            },
        )

    def step(self, action: TicketAction) -> TicketObservation:
        if self._state.is_done:
            return self._build_done_obs("Episode already done. Call reset() to start a new episode.")

        self._state.step_count += 1
        ticket = self._current_ticket
        gt = ticket["ground_truth"]
        action_dict = action.model_dump()

        if self._task_id == "task_1_classify":
            reward, scores, feedback = grade_task1(action_dict, gt)
        elif self._task_id == "task_2_respond":
            reward, scores, feedback = grade_task2(action_dict, gt, ticket)
        else:
            reward, scores, feedback = grade_task3(action_dict, gt, ticket)

        self._state.cumulative_reward += reward
        self._state.is_done = True

        return TicketObservation(
            ticket_id=ticket["ticket_id"],
            ticket_subject=ticket["subject"],
            ticket_body=ticket["body"],
            customer_name=ticket["customer_name"],
            customer_tier=ticket["customer_tier"],
            created_at=ticket["created_at"],
            feedback=feedback,
            reward=reward,
            done=True,
            step_count=self._state.step_count,
            scores=scores,
            metadata={
                "task_id": self._task_id,
                "episode_id": self._state.episode_id,
                "cumulative_reward": self._state.cumulative_reward,
            },
        )

    def state(self) -> TicketState:
        return self._state

    def _build_done_obs(self, feedback: str) -> TicketObservation:
        ticket = self._current_ticket or {}
        return TicketObservation(
            ticket_id=ticket.get("ticket_id", ""),
            ticket_subject=ticket.get("subject", ""),
            ticket_body=ticket.get("body", ""),
            customer_name=ticket.get("customer_name", ""),
            customer_tier=ticket.get("customer_tier", ""),
            created_at=ticket.get("created_at", ""),
            feedback=feedback,
            reward=0.0,
            done=True,
            step_count=self._state.step_count,
            scores={},
            metadata={},
        )

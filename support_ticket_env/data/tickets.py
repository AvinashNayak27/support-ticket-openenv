"""Static ticket dataset used across all tasks."""
from __future__ import annotations
from typing import List, Dict, Any

TICKETS: List[Dict[str, Any]] = [
    {
        "ticket_id": "TKT-001",
        "subject": "Cannot login to my account",
        "body": (
            "Hi, I've been trying to log into my account for the past 2 hours but keep getting "
            "'Invalid credentials' even though I just reset my password. My account is linked to "
            "john.doe@example.com. This is extremely urgent as I have a presentation in 1 hour "
            "that requires access to my files."
        ),
        "customer_name": "John Doe",
        "customer_tier": "enterprise",
        "created_at": "2024-01-15T09:00:00Z",
        "ground_truth": {
            "category": "account",
            "priority": "critical",
            "key_issues": ["login failure", "password reset not working", "time-sensitive"],
            "resolution_steps": [
                "Verify customer identity via email",
                "Check account status in admin panel",
                "Force password reset and clear session tokens",
                "Confirm customer can login",
                "Escalate to engineering if auth system issue detected"
            ],
            "response_keywords": ["reset", "password", "account", "help", "urgency", "minutes"],
        },
    },
    {
        "ticket_id": "TKT-002",
        "subject": "Invoice shows wrong amount",
        "body": (
            "Hello, I was charged $299 this month but my plan is only $99/month. "
            "I did not authorize any additional charges. Please refund the difference immediately. "
            "My account number is ACC-44821."
        ),
        "customer_name": "Sarah Chen",
        "customer_tier": "pro",
        "created_at": "2024-01-15T10:30:00Z",
        "ground_truth": {
            "category": "billing",
            "priority": "high",
            "key_issues": ["overcharge", "unauthorized charge", "refund requested"],
            "resolution_steps": [
                "Pull billing history for ACC-44821",
                "Identify the source of the $200 discrepancy",
                "Issue refund if charge was in error",
                "Send refund confirmation email",
                "Add note to prevent recurrence"
            ],
            "response_keywords": ["refund", "invoice", "billing", "review", "apologize"],
        },
    },
    {
        "ticket_id": "TKT-003",
        "subject": "API rate limit errors on free plan",
        "body": (
            "I keep getting 429 Too Many Requests errors even though I'm well within the "
            "documented 1000 req/hour limit. I'm only making about 200 requests per hour. "
            "My API key is pk_live_abc123. Started happening around 2pm UTC today."
        ),
        "customer_name": "Dev Team",
        "customer_tier": "free",
        "created_at": "2024-01-15T14:15:00Z",
        "ground_truth": {
            "category": "technical",
            "priority": "medium",
            "key_issues": ["rate limit error", "429 errors", "API key issue"],
            "resolution_steps": [
                "Check API key usage metrics in dashboard",
                "Verify rate limit counter is resetting correctly",
                "Check if there's a burst limit separate from hourly",
                "Review API key for any flags or restrictions",
                "Provide technical explanation and workaround"
            ],
            "response_keywords": ["rate limit", "API", "investigate", "429", "usage"],
        },
    },
    {
        "ticket_id": "TKT-004",
        "subject": "Order not delivered after 3 weeks",
        "body": (
            "I placed order #ORD-88291 three weeks ago and it still hasn't arrived. "
            "The tracking number TS928471US shows 'In Transit' since January 5th. "
            "I need this for an event this weekend. Can you please expedite or replace?"
        ),
        "customer_name": "Maria Garcia",
        "customer_tier": "free",
        "created_at": "2024-01-16T08:00:00Z",
        "ground_truth": {
            "category": "shipping",
            "priority": "high",
            "key_issues": ["delayed delivery", "tracking stuck", "event deadline"],
            "resolution_steps": [
                "Check carrier portal for TS928471US status",
                "Contact shipping carrier directly",
                "Offer replacement shipment or refund",
                "Expedite new shipment if replacement chosen",
                "Follow up within 24 hours"
            ],
            "response_keywords": ["tracking", "shipping", "replacement", "expedite", "sorry"],
        },
    },
    {
        "ticket_id": "TKT-005",
        "subject": "How do I export my data?",
        "body": (
            "Hi there, I'd like to export all my data from the platform. "
            "I've looked through the settings but can't find an export option. "
            "Is this a feature that exists? If so, where is it?"
        ),
        "customer_name": "Alex Kim",
        "customer_tier": "pro",
        "created_at": "2024-01-16T11:00:00Z",
        "ground_truth": {
            "category": "general",
            "priority": "low",
            "key_issues": ["data export", "feature inquiry"],
            "resolution_steps": [
                "Confirm data export feature exists",
                "Provide step-by-step navigation guide",
                "Mention export formats available",
                "Offer to initiate export if needed"
            ],
            "response_keywords": ["export", "settings", "data", "steps", "format"],
        },
    },
]

TICKET_INDEX: Dict[str, Dict[str, Any]] = {t["ticket_id"]: t for t in TICKETS}

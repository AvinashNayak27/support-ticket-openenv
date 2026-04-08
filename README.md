---
title: Support Ticket Openenv
emoji: 📚
colorFrom: red
colorTo: green
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Support Ticket OpenEnv Environment

A real-world **Customer Support Ticket Management** environment built on the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) framework. An AI agent learns to triage, respond to, and resolve customer support tickets across three tasks of increasing difficulty.

---

## Environment Overview

| Field | Value |
|---|---|
| **Domain** | Customer Support / NLP |
| **Tasks** | 3 (Easy -> Medium -> Hard) |
| **Episode type** | Single-step (1 action per episode) |
| **Reward range** | 0.0 - 1.0 |
| **Action space** | Structured JSON (category, priority, response, resolution) |
| **Observation space** | Ticket content + grading feedback |

---

## Tasks

### Task 1 - Ticket Classification (Easy)
**Goal:** Classify a support ticket by category and priority.

| Field | Values |
|---|---|
| `category` | `billing` | `technical` | `account` | `shipping` | `general` |
| `priority` | `low` | `medium` | `high` | `critical` |

**Scoring:**
- Correct category: +0.50
- Correct priority: +0.50 (partial +0.25 if off by 1 level)

---

### Task 2 - Response Drafting (Medium)
**Goal:** Draft a professional, empathetic response to the customer.

**Scoring:**
| Component | Weight |
|---|---|
| Keyword coverage (domain-relevant terms) | 0.40 |
| Personalization (uses customer name) | 0.20 |
| Professionalism (polite opener + closer) | 0.20 |
| Length (50-500 words) | 0.20 |

---

### Task 3 - Full Resolution Pipeline (Hard)
**Goal:** Classify + respond + provide a complete internal resolution plan.

**Scoring:**
| Component | Weight |
|---|---|
| Classification (scaled from Task 1) | 0.20 |
| Response quality (scaled from Task 2) | 0.30 |
| Resolution steps coverage | 0.30 |
| Resolution correctness (resolved=True + summary) | 0.20 |

---

## Setup & Installation

### Local Development

```bash
git clone https://github.com/AvinashNayak27/support-ticket-openenv
cd support-ticket-openenv
pip install -e .
python -m uvicorn support_ticket_env.server.app:app --host 0.0.0.0 --port 7860 --reload
```

### Docker

```bash
docker build -f server/Dockerfile -t support-ticket-env .
docker run -p 7860:7860 support-ticket-env
```

---

## Running Inference

```bash

python inference.py
```

## License

MIT

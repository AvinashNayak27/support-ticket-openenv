#!/usr/bin/env python3
"""
Pre-submission validation script for the Support Ticket OpenEnv environment.
Run: python validate.py
All checks must pass (PASS).
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

PASS = "[PASS]"
FAIL = "[FAIL]"

results = []


def check(name: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    msg = f"{status} {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    results.append(passed)
    return passed


print("\n=== 1. Required Files ===")
required_files = [
    "openenv.yaml", "pyproject.toml", "inference.py", "validate.py",
    "server/Dockerfile", "server/requirements.txt",
    "support_ticket_env/__init__.py", "support_ticket_env/models.py",
    "support_ticket_env/data/__init__.py", "support_ticket_env/data/tickets.py",
    "support_ticket_env/graders/__init__.py",
    "support_ticket_env/graders/task1_grader.py",
    "support_ticket_env/graders/task2_grader.py",
    "support_ticket_env/graders/task3_grader.py",
    "support_ticket_env/server/__init__.py",
    "support_ticket_env/server/app.py",
    "support_ticket_env/server/environment.py",
    "README.md",
]
missing = [f for f in required_files if not (ROOT / f).exists()]
check("Required files present", len(missing) == 0,
      f"Missing: {missing}" if missing else f"All {len(required_files)} files present")

print("\n=== 2. Module Imports ===")
modules = [
    "support_ticket_env", "support_ticket_env.models",
    "support_ticket_env.data", "support_ticket_env.data.tickets",
    "support_ticket_env.graders",
    "support_ticket_env.graders.task1_grader",
    "support_ticket_env.graders.task2_grader",
    "support_ticket_env.graders.task3_grader",
    "support_ticket_env.server.environment",
    "support_ticket_env.server.app",
]
for mod in modules:
    try:
        importlib.import_module(mod)
        check(f"Import {mod}", True)
    except Exception as e:
        check(f"Import {mod}", False, str(e))

print("\n=== 3. Graders ===")
try:
    from support_ticket_env.graders import grade_task1, grade_task2, grade_task3
    from support_ticket_env.data.tickets import TICKET_INDEX
    ticket = TICKET_INDEX["TKT-001"]
    gt = ticket["ground_truth"]
    r, _, _ = grade_task1({"category": "account", "priority": "critical"}, gt)
    check("Task1 perfect score", abs(r - 1.0) < 0.01, f"score={r}")
    r, _, _ = grade_task1({"category": "account", "priority": "high"}, gt)
    check("Task1 partial score", abs(r - 0.75) < 0.01, f"score={r}")
except Exception as e:
    check("Grader tests", False, str(e))

print("\n" + "="*50)
total = len(results)
passed = sum(results)
print(f"Results: {passed}/{total} checks passed")
if passed < total:
    sys.exit(1)
else:
    print("All checks passed! Ready to submit.")

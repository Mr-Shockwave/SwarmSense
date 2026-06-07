#!/usr/bin/env python3
"""Smoke test for per-rover manager agents + Redis tools.

Run from backend/:
  python test_rover_agents.py --dry-run     # no OpenAI
  python test_rover_agents.py               # full LLM run (needs OPENAI_API_KEY)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# CrewAI logs emoji on Windows consoles; force UTF-8 when possible.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from config import GRID_HEIGHT, GRID_WIDTH, settings
from tools.redis_tools import (
    is_using_mock_redis,
    redis_get_raw,
    redis_publish_raw,
    redis_set_raw,
    reset_redis_client,
)

from agents.rover_managers import (
    build_rover1_crew,
    build_rover2_crew,
    print_dry_run_report,
    run_manager_dry,
)


def seed_mission_state() -> None:
    """Seed Redis with mission data and left/right zones."""
    mid = GRID_WIDTH // 2
    redis_set_raw("mission:goal", "Explore the grid and find objects matching criteria")
    redis_set_raw("mission:criteria", "small reflective metal object")
    redis_set_raw("mission:status", "running")
    redis_set_raw(
        "rover1:zone",
        {"x_min": 0, "x_max": mid - 1, "y_min": 0, "y_max": GRID_HEIGHT - 1},
    )
    redis_set_raw(
        "rover2:zone",
        {"x_min": mid, "x_max": GRID_WIDTH - 1, "y_min": 0, "y_max": GRID_HEIGHT - 1},
    )
    redis_set_raw("rover1:position", {"x": 0, "y": 0, "heading": 90})
    redis_set_raw("rover2:position", {"x": mid, "y": 0, "heading": 90})
    redis_set_raw("targets:assignments", {})


def test_redis_tools() -> None:
    print("\n=== Redis tools smoke test ===")
    redis_set_raw("test:key", {"hello": "roverswarm"})
    assert redis_get_raw("test:key") == {"hello": "roverswarm"}
    redis_publish_raw("test:channel", {"ping": 1})
    print(f"  backend: {'in-memory mock' if is_using_mock_redis() else settings.REDIS_URL}")
    print("  redis_get / redis_set / redis_publish OK")


def run_dry() -> None:
    reset_redis_client()
    seed_mission_state()
    test_redis_tools()
    for rover_id in ("rover1", "rover2"):
        report = run_manager_dry(rover_id)
        print_dry_run_report(rover_id, report)
    print("\n=== dry-run complete ===")


def run_full() -> None:
    if not settings.OPENAI_API_KEY:
        print("OPENAI_API_KEY missing — use --dry-run or set the key in .env", file=sys.stderr)
        sys.exit(1)

    reset_redis_client()
    seed_mission_state()
    print(f"\nRedis: {'in-memory mock' if is_using_mock_redis() else settings.REDIS_URL}")
    print("Seeded mission + zones (rover1=left, rover2=right)\n")

    for label, build_crew in (("rover1", build_rover1_crew), ("rover2", build_rover2_crew)):
        print(f"=== kicking off {label} manager crew ===")
        crew = build_crew()
        result = crew.kickoff()
        print(f"\n--- {label} manager result ---")
        print(result)
        status = redis_get_raw(f"{label}:status")
        print(f"--- {label}:status in Redis ---")
        print(json.dumps(status, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Test per-rover manager agents")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exercise Redis tools + stub subagents only (no OpenAI)",
    )
    args = parser.parse_args()
    if args.dry_run:
        run_dry()
    else:
        run_full()


if __name__ == "__main__":
    main()

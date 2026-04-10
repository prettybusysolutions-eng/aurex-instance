#!/usr/bin/env python3
"""
task_router.py — Route CSMR tasks to the most appropriate model.

Usage:
    python3 task_router.py --task attribution --tokens 80000
    python3 task_router.py --task code_task --tokens 5000
    python3 task_router.py --task user_chat --tokens 1000
"""
import argparse
import json
import os
import sys

ROUTER_CONFIG = os.path.join(os.path.dirname(__file__), "task-router.json")
DEFAULT_MODEL = "anthropic/claude-sonnet-4-6"


def load_routes() -> list:
    try:
        with open(ROUTER_CONFIG) as f:
            data = json.load(f)
        return data.get("routes", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_model_for_task(task_type: str, estimated_tokens: int = 0) -> str:
    """
    Return the model ID for the best matching route given a task_type and
    optional estimated_tokens.  Falls back to DEFAULT_MODEL if no match.
    """
    routes = load_routes()
    if not routes:
        return DEFAULT_MODEL

    for route in routes:
        triggers = route.get("triggers", [])
        min_tokens = route.get("min_context_tokens", 0)
        if task_type in triggers:
            # If route has a min_context_tokens gate, only use it when above threshold
            if min_tokens > 0 and estimated_tokens < min_tokens:
                # Still a trigger match but below context floor — keep scanning
                continue
            return route["model"]

    # Second pass: any trigger match regardless of token count
    for route in routes:
        if task_type in route.get("triggers", []):
            return route["model"]

    return DEFAULT_MODEL


def get_route_info(task_type: str, estimated_tokens: int = 0) -> dict:
    """Return the full route dict for a task_type, or a synthetic default."""
    routes = load_routes()
    for route in routes:
        triggers = route.get("triggers", [])
        min_tokens = route.get("min_context_tokens", 0)
        if task_type in triggers:
            if min_tokens > 0 and estimated_tokens < min_tokens:
                continue
            return route
    for route in routes:
        if task_type in route.get("triggers", []):
            return route
    return {
        "id": "default-primary",
        "model": DEFAULT_MODEL,
        "alias": "claude-sonnet",
        "cost_tier": "paid",
        "context_window": 200000,
    }


def main():
    parser = argparse.ArgumentParser(description="Route a CSMR task to the right model.")
    parser.add_argument("--task", required=True, help="Task type trigger string (e.g. attribution, code_task)")
    parser.add_argument("--tokens", type=int, default=0, help="Estimated context token count")
    parser.add_argument("--json", action="store_true", help="Output full route JSON instead of just model ID")
    args = parser.parse_args()

    if args.json:
        info = get_route_info(args.task, args.tokens)
        print(json.dumps(info, indent=2))
    else:
        model = get_model_for_task(args.task, args.tokens)
        print(model)


if __name__ == "__main__":
    main()

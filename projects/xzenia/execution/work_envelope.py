#!/usr/bin/env python3
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class WorkEnvelope:
    work_id: str
    source: str
    priority: int
    checkpoint_state: dict[str, Any]
    expected_outcome: dict[str, Any]
    rollback_plan: dict[str, Any] = field(default_factory=dict)
    verification_contract: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().astimezone().isoformat())

    def to_dict(self):
        return asdict(self)


def main():
    payload = json.loads(sys.stdin.read())
    env = WorkEnvelope(**payload)
    print(json.dumps(env.to_dict(), indent=2))


if __name__ == '__main__':
    main()

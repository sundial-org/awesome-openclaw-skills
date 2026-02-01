import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class State:
    dismissed: Dict[str, float]
    snoozed_until: Dict[str, float]


def load_state(path: str) -> State:
    if not os.path.exists(path):
        return State(dismissed={}, snoozed_until={})
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return State(
        dismissed=data.get("dismissed", {}),
        snoozed_until=data.get("snoozed_until", {}),
    )


def save_state(path: str, state: State) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "dismissed": state.dismissed,
                "snoozed_until": state.snoozed_until,
                "updated_at": time.time(),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def is_snoozed(state: State, key: str, now: float | None = None) -> bool:
    now = now or time.time()
    until = state.snoozed_until.get(key)
    return bool(until and until > now)

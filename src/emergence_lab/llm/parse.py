"""Parse a single action token from raw LLM text. No intelligence claims."""

from __future__ import annotations

import re

from emergence_lab.world.types import Action

_TAG = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

_TOKEN = {
    "NORTH": Action.MOVE_NORTH,
    "SOUTH": Action.MOVE_SOUTH,
    "EAST": Action.MOVE_EAST,
    "WEST": Action.MOVE_WEST,
    "STAY": Action.STAY,
    "MOVE_NORTH": Action.MOVE_NORTH,
    "MOVE_SOUTH": Action.MOVE_SOUTH,
    "MOVE_EAST": Action.MOVE_EAST,
    "MOVE_WEST": Action.MOVE_WEST,
}

_WORD = re.compile(
    r"\b(MOVE_NORTH|MOVE_SOUTH|MOVE_EAST|MOVE_WEST|NORTH|SOUTH|EAST|WEST|STAY)\b",
    re.IGNORECASE,
)


def strip_thinking(text: str) -> str:
    return _TAG.sub(" ", text)


def parse_action(raw: str) -> Action | None:
    """Return the last explicit action token, or None if none found."""
    cleaned = strip_thinking(raw or "")
    matches = list(_WORD.finditer(cleaned))
    if not matches:
        return None
    token = matches[-1].group(1).upper()
    return _TOKEN.get(token)

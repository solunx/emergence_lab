"""Parse a single action token from raw LLM text. No intelligence claims."""

from __future__ import annotations

import re
from dataclasses import dataclass

from emergence_lab.world.types import Action

_TAG = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_MEMORY_LINE = re.compile(r"(?im)^\s*MEMORY:\s*(.*)$")

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


@dataclass(frozen=True)
class ParsedLlmOutput:
    action: Action | None
    memory_write: str | None


def strip_thinking(text: str) -> str:
    return _TAG.sub(" ", text)


def parse_memory_write(raw: str) -> str | None:
    cleaned = strip_thinking(raw or "")
    match = _MEMORY_LINE.search(cleaned)
    if not match:
        return None
    text = match.group(1).strip()
    return text or None


def strip_memory_lines(text: str) -> str:
    return _MEMORY_LINE.sub("", text)


def parse_action(raw: str) -> Action | None:
    """Return the last explicit action token, or None if none found.

    MEMORY: lines are stripped first so a note that mentions EAST/STAY
    cannot steal the action token.
    """
    cleaned = strip_memory_lines(strip_thinking(raw or ""))
    matches = list(_WORD.finditer(cleaned))
    if not matches:
        return None
    token = matches[-1].group(1).upper()
    return _TOKEN.get(token)


def parse_llm_output(raw: str) -> ParsedLlmOutput:
    return ParsedLlmOutput(action=parse_action(raw), memory_write=parse_memory_write(raw))

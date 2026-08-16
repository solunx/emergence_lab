"""Prompt templates live here, not in the LLM controller class."""

from __future__ import annotations

import hashlib

PROMPT_VERSION = 1

LLM_A = """Choose exactly one valid action based only on the observation. Reply with exactly one of: NORTH, SOUTH, EAST, WEST, STAY.

Observation:
{observation}
"""

LLM_B = """Your objective is to remain alive as long as possible. Choose exactly one valid action based only on the observation. Reply with exactly one of: NORTH, SOUTH, EAST, WEST, STAY.

Observation:
{observation}
"""

PROMPTS = {
    "llm_a": LLM_A,
    "llm": LLM_A,
    "llm_b": LLM_B,
}


def prompt_text(prompt_id: str, observation_block: str) -> str:
    template = PROMPTS.get(prompt_id)
    if template is None:
        raise ValueError(f"unknown prompt_id: {prompt_id}")
    return template.format(observation=observation_block)


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

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

LLM_A_MEMORY = """Choose exactly one valid action based only on the observation and your memory. Reply with exactly one of: NORTH, SOUTH, EAST, WEST, STAY on the first line. Optionally add a second line MEMORY: <one short note to keep>. Omit MEMORY to write nothing.

Observation:
{observation}

Memory:
{memory}
"""

LLM_B_MEMORY = """Your objective is to remain alive as long as possible. Choose exactly one valid action based only on the observation and your memory. Reply with exactly one of: NORTH, SOUTH, EAST, WEST, STAY on the first line. Optionally add a second line MEMORY: <one short note to keep>. Omit MEMORY to write nothing.

Observation:
{observation}

Memory:
{memory}
"""

PROMPTS = {
    "llm_a": LLM_A,
    "llm": LLM_A,
    "llm_b": LLM_B,
    "llm_a_memory": LLM_A_MEMORY,
    "llm_memory": LLM_A_MEMORY,
    "llm_b_memory": LLM_B_MEMORY,
}

MEMORY_PROMPT_IDS = frozenset({"llm_a_memory", "llm_memory", "llm_b_memory"})


def format_memory(memory: list[str] | None) -> str:
    if not memory:
        return "(empty)"
    return "\n".join(f"- {item}" for item in memory)


def prompt_text(
    prompt_id: str,
    observation_block: str,
    memory: list[str] | None = None,
) -> str:
    template = PROMPTS.get(prompt_id)
    if template is None:
        raise ValueError(f"unknown prompt_id: {prompt_id}")
    kwargs: dict[str, str] = {"observation": observation_block}
    if "{memory}" in template:
        kwargs["memory"] = format_memory(memory)
    return template.format(**kwargs)


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

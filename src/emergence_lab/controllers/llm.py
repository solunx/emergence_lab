"""C3: LLM as a decision function. Prompts come from config, not this class."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from emergence_lab.config import SimConfig
from emergence_lab.controllers.base import Controller, Decision
from emergence_lab.llm.ollama import LlmClient, LlmResponse, OllamaClient
from emergence_lab.llm.parse import parse_action
from emergence_lab.llm.prompts import PROMPTS, prompt_hash, prompt_text
from emergence_lab.world.observation import Observation
from emergence_lab.world.types import Action


def format_observation(observation: Observation) -> str:
    actions = ", ".join(
        action.value.replace("MOVE_", "") for action in observation.available_actions
    )
    return (
        f"{observation.ascii()}\n"
        f"Energy: {observation.energy}\n"
        f"Age: {observation.age}\n"
        f"Available actions: {actions}\n"
        "Legend: A=you, F=resource, O=other organism, .=empty. North is up."
    )


class LlmController(Controller):
    def __init__(
        self,
        config: SimConfig,
        client: LlmClient | None = None,
    ) -> None:
        self.config = config
        self.prompt_id = config.llm_prompt_id or "llm_a"
        self.prompt_version = config.llm_prompt_version
        if client is not None:
            self.client = client
        else:
            self.client = OllamaClient(
                model=config.llm_model or "",
                endpoint=config.llm_endpoint,
                temperature=config.llm_temperature,
                num_predict=config.llm_num_predict,
                timeout_s=config.llm_timeout_s,
            )

    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        block = format_observation(observation)
        if memory:
            block += "\nMemory:\n" + "\n".join(f"- {item}" for item in memory)
        prompt = prompt_text(self.prompt_id, block)
        started = time.perf_counter()
        response: LlmResponse = self.client.complete(prompt)
        latency_ms = (time.perf_counter() - started) * 1000.0
        parsed = parse_action(response.text)
        invalid = parsed is None
        action = parsed if parsed is not None else Action.STAY
        trace = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "system_prompt_hash": prompt_hash(PROMPTS[self.prompt_id]),
            "model": response.model or self.config.llm_model,
            "model_config": {
                "endpoint": self.config.llm_endpoint,
                "temperature": self.config.llm_temperature,
                "num_predict": self.config.llm_num_predict,
            },
            "raw_output": response.text,
            "parsed_action": None if parsed is None else parsed.value,
            "self_reported_rationale": None,
            "latency_ms": round(latency_ms, 3),
            "input_tokens": response.prompt_tokens,
            "output_tokens": response.completion_tokens,
            "valid": not invalid,
            "fallback": "STAY" if invalid else None,
        }
        return Decision(action=action, invalid=invalid, llm_trace=trace)

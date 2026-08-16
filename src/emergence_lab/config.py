"""Experiment configuration. No experimental parameters are hardcoded in the engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONTROLLER_REPRODUCTION = {
    "random": False,
    "random_r": True,
    "reactive": False,
    "reactive_r": True,
    "evolutionary": True,
    "evolutionary_oracle": False,
    "evolutionary_oracle_r": True,
    "llm": False,
    "llm_a": False,
    "llm_b": False,
    "always_stay": False,
    "always_north": False,
}

CONTROLLER_GENOME = {
    "random": False,
    "random_r": False,
    "reactive": False,
    "reactive_r": False,
    "evolutionary": True,
    "evolutionary_oracle": False,
    "evolutionary_oracle_r": False,
    "llm": False,
    "llm_a": False,
    "llm_b": False,
    "always_stay": False,
    "always_north": False,
}

# Named experiment conditions share a decision class. `_r` means reproduction
# without a genome (C0-R / C1-R ablations). llm / llm_a = prompt A; llm_b = prompt B.
DECISION_CONTROLLER = {
    "random": "random",
    "random_r": "random",
    "reactive": "reactive",
    "reactive_r": "reactive",
    "evolutionary": "evolutionary",
    "evolutionary_oracle": "evolutionary_oracle",
    "evolutionary_oracle_r": "evolutionary_oracle",
    "llm": "llm",
    "llm_a": "llm",
    "llm_b": "llm",
    "always_stay": "always_stay",
    "always_north": "always_north",
}

CONTROLLER_PROMPT = {
    "llm": "llm_a",
    "llm_a": "llm_a",
    "llm_b": "llm_b",
}

LLM_CONTROLLERS = frozenset(CONTROLLER_PROMPT)

DEFAULT_LLM_ENDPOINT = "http://127.0.0.1:11434"


@dataclass
class SimConfig:
    width: int = 32
    height: int = 32
    torus: bool = True
    resource_count: int = 20
    resource_value: int = 30
    regen_delay: int = 15
    initial_population: int = 10
    ticks: int = 1000
    initial_energy: int = 100
    base_metabolism: int = 1
    movement_cost: int = 1
    reproduction_energy_threshold: int = 150
    reproduction_cost: int = 75
    observation_radius: int = 2
    mutation_probability: float = 0.05
    mutation_strength: float = 0.1
    genome_init_low: float = -0.1
    genome_init_high: float = 0.1
    memory_capacity: int = 20
    memory_entry_max_chars: int = 200
    seed: int = 123456
    controller: str = "random"
    experiment_id: str = "milestone1"
    snapshot_every: int = 100
    reproduction_enabled: bool | None = None
    genome_enabled: bool | None = None
    llm_model: str | None = None
    llm_endpoint: str = DEFAULT_LLM_ENDPOINT
    llm_temperature: float = 0.0
    llm_prompt_id: str | None = None
    llm_prompt_version: int = 1
    llm_timeout_s: float = 120.0
    llm_num_predict: int = 64
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.reproduction_enabled is None:
            self.reproduction_enabled = CONTROLLER_REPRODUCTION.get(self.controller, False)
        if self.genome_enabled is None:
            self.genome_enabled = CONTROLLER_GENOME.get(self.controller, False)
        if self.controller in ("llm_a", "llm_b"):
            self.llm_prompt_id = CONTROLLER_PROMPT[self.controller]
        elif self.llm_prompt_id is None:
            self.llm_prompt_id = CONTROLLER_PROMPT.get(self.controller, "llm_a")
        if not self.llm_endpoint:
            self.llm_endpoint = DEFAULT_LLM_ENDPOINT

    def to_dict(self) -> dict:
        data = asdict(self)
        data["reproduction_enabled"] = bool(self.reproduction_enabled)
        data["genome_enabled"] = bool(self.genome_enabled)
        return data

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> SimConfig:
        world = raw.get("world", {})
        population = raw.get("population", {})
        simulation = raw.get("simulation", {})
        organism = raw.get("organism", {})
        observation = raw.get("observation", {})
        controller = raw.get("controller", {})
        experiment = raw.get("experiment", {})
        llm = raw.get("llm") or {}
        endpoint = llm.get("endpoint") or DEFAULT_LLM_ENDPOINT
        return cls(
            width=world.get("width", 32),
            height=world.get("height", 32),
            torus=world.get("torus", True),
            resource_count=world.get("resource_count", world.get("resources", 20)),
            resource_value=world.get("resource_value", 30),
            regen_delay=world.get("regen_delay", 15),
            initial_population=population.get("initial_size", 10),
            ticks=simulation.get("ticks", 1000),
            initial_energy=organism.get("initial_energy", 100),
            base_metabolism=organism.get("base_metabolism", 1),
            movement_cost=organism.get("movement_cost", 1),
            reproduction_energy_threshold=organism.get(
                "reproduction_energy_threshold", 150
            ),
            reproduction_cost=organism.get("reproduction_cost", 75),
            observation_radius=observation.get("radius", 2),
            mutation_probability=organism.get("mutation_probability", 0.05),
            mutation_strength=organism.get("mutation_strength", 0.1),
            seed=experiment.get("seed", 123456),
            controller=controller.get("type", "random"),
            experiment_id=experiment.get("experiment_id", "milestone1"),
            snapshot_every=simulation.get("snapshot_every", 100),
            llm_model=llm.get("model"),
            llm_endpoint=endpoint,
            llm_temperature=float(llm.get("temperature", 0.0)),
            llm_prompt_id=llm.get("prompt_id"),
            llm_prompt_version=int(llm.get("prompt_version", 1)),
            llm_timeout_s=float(llm.get("timeout_s", 120.0)),
            llm_num_predict=int(llm.get("num_predict", 64)),
            extra=raw,
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> SimConfig:
        with Path(path).open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        return cls.from_mapping(raw)

from __future__ import annotations

from dataclasses import dataclass

from emergence_lab.world.observation import Observation
from emergence_lab.world.types import Action


@dataclass(frozen=True)
class Decision:
    action: Action
    memory_write: str | None = None
    rationale: str | None = None


class Controller:
    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        raise NotImplementedError

from __future__ import annotations

import random

from emergence_lab.controllers.base import Controller, Decision
from emergence_lab.world.observation import Observation


class RandomController(Controller):
    """Random-controller baseline. Ignores the observation besides available actions."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        action = self.rng.choice(list(observation.available_actions))
        return Decision(action=action)

from __future__ import annotations

import random

from emergence_lab.controllers.base import Controller, Decision
from emergence_lab.world.observation import Observation
from emergence_lab.world.types import Action, CellKind


class ReactiveController(Controller):
    """Hand-coded food-seeking heuristic. No N-S-E-W priority bias."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        radius = len(observation.cells) // 2
        resources: list[tuple[int, int, int]] = []
        for row, line in enumerate(observation.cells):
            for col, cell in enumerate(line):
                if cell is CellKind.RESOURCE:
                    dx = col - radius
                    dy = radius - row
                    dist = abs(dx) + abs(dy)
                    resources.append((dist, dx, dy))
        if not resources:
            action = self.rng.choice(list(observation.available_actions))
            return Decision(action=action)

        min_dist = min(item[0] for item in resources)
        closest = [item for item in resources if item[0] == min_dist]
        _, dx, dy = closest[self.rng.randrange(len(closest))]

        candidates: list[Action] = []
        if dy > 0:
            candidates.append(Action.MOVE_NORTH)
        if dy < 0:
            candidates.append(Action.MOVE_SOUTH)
        if dx > 0:
            candidates.append(Action.MOVE_EAST)
        if dx < 0:
            candidates.append(Action.MOVE_WEST)
        if not candidates:
            action = self.rng.choice(list(observation.available_actions))
            return Decision(action=action)
        action = candidates[self.rng.randrange(len(candidates))]
        return Decision(action=action)

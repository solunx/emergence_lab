"""Engine-validation controllers. Not part of the experimental matrix."""

from __future__ import annotations

from emergence_lab.controllers.base import Controller, Decision
from emergence_lab.world.observation import Observation
from emergence_lab.world.types import Action


class AlwaysStayController(Controller):
    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        return Decision(action=Action.STAY)


class AlwaysNorthController(Controller):
    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        return Decision(action=Action.MOVE_NORTH)

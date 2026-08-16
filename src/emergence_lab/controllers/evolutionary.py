from __future__ import annotations

import random

from emergence_lab.controllers.base import Controller, Decision
from emergence_lab.world.observation import Observation
from emergence_lab.world.types import (
    ALL_ACTIONS,
    N_FEATURES,
    N_GENOME_WEIGHTS,
    Action,
    CellKind,
)

# Egocentric rays: two cells along each cardinal axis.
# Observation row 0 is north, col 0 is west, center is (radius, radius).
_RAYS = {
    "N": ((-1, 0), (-2, 0)),  # (drow, dcol) from center; negative row = north
    "S": ((1, 0), (2, 0)),
    "E": ((0, 1), (0, 2)),
    "W": ((0, -1), (0, -2)),
}


def extract_features(observation: Observation) -> tuple[float, ...]:
    radius = len(observation.cells) // 2
    center = (radius, radius)

    def present(kind: CellKind, direction: str) -> float:
        for drow, dcol in _RAYS[direction]:
            row = center[0] + drow
            col = center[1] + dcol
            if 0 <= row < len(observation.cells) and 0 <= col < len(observation.cells):
                if observation.cells[row][col] is kind:
                    return 1.0
        return 0.0

    return (
        present(CellKind.RESOURCE, "N"),
        present(CellKind.RESOURCE, "S"),
        present(CellKind.RESOURCE, "E"),
        present(CellKind.RESOURCE, "W"),
        present(CellKind.ORGANISM, "N"),
        present(CellKind.ORGANISM, "S"),
        present(CellKind.ORGANISM, "E"),
        present(CellKind.ORGANISM, "W"),
        1.0,
    )


def cardinal_oracle_genome() -> tuple[float, ...]:
    """Hand-set 45 weights: resource on an axis → move that way. No food prior on diagonals.

    Bias and organism weights are 0, so an empty or diagonal-only patch ties all
    five actions (uniform via controller_rng). This is a diagnostic phenotype,
    not a fitted copy of C1 and not a new C2 feature set.
    """
    weights = [0.0] * N_GENOME_WEIGHTS
    for action_index, feature_index in ((0, 0), (1, 1), (2, 2), (3, 3)):
        weights[action_index * N_FEATURES + feature_index] = 1.0
    return tuple(weights)


def mutate_genome(
    genome: tuple[float, ...],
    rng: random.Random,
    probability: float,
    strength: float,
) -> tuple[float, ...]:
    child = []
    for weight in genome:
        if rng.random() < probability:
            child.append(weight + rng.gauss(0.0, strength))
        else:
            child.append(weight)
    return tuple(child)


class EvolutionaryController(Controller):
    """Linear policy over 9 local features. No hidden exploration term."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        if genome is None:
            raise ValueError("evolutionary controller requires a genome")
        features = extract_features(observation)
        scores: list[float] = []
        for action_index, _action in enumerate(ALL_ACTIONS):
            score = 0.0
            for feature_index, feature in enumerate(features):
                weight = genome[action_index * N_FEATURES + feature_index]
                score += weight * feature
            scores.append(score)
        best = max(scores)
        winners = [
            action
            for action, score in zip(ALL_ACTIONS, scores, strict=True)
            if score == best
        ]
        action: Action = winners[self.rng.randrange(len(winners))]
        return Decision(action=action)


class EvolutionaryOracleController(EvolutionaryController):
    """Same 9 features and linear argmax as C2; weights fixed, not evolved."""

    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        return super().decide(
            observation,
            genome=cardinal_oracle_genome(),
            memory=memory,
        )

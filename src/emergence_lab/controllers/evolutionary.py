from __future__ import annotations

import random

from emergence_lab.controllers.base import Controller, Decision
from emergence_lab.world.observation import Observation
from emergence_lab.world.types import (
    ALL_ACTIONS,
    DIAG_N_FEATURES,
    DIAG_N_GENOME_WEIGHTS,
    N_FEATURES,
    N_GENOME_WEIGHTS,
    Action,
    CellKind,
)

# Egocentric rays: two cells along each axis / diagonal.
# Observation row 0 is north, col 0 is west, center is (radius, radius).
_RAYS = {
    "N": ((-1, 0), (-2, 0)),
    "S": ((1, 0), (2, 0)),
    "E": ((0, 1), (0, 2)),
    "W": ((0, -1), (0, -2)),
    "NE": ((-1, 1), (-2, 2)),
    "SE": ((1, 1), (2, 2)),
    "SW": ((1, -1), (2, -2)),
    "NW": ((-1, -1), (-2, -2)),
}


def _present(observation: Observation, kind: CellKind, direction: str) -> float:
    radius = len(observation.cells) // 2
    center = (radius, radius)
    for drow, dcol in _RAYS[direction]:
        row = center[0] + drow
        col = center[1] + dcol
        if 0 <= row < len(observation.cells) and 0 <= col < len(observation.cells):
            if observation.cells[row][col] is kind:
                return 1.0
    return 0.0


def extract_features(observation: Observation) -> tuple[float, ...]:
    """v0.1 C2: 9 features (cardinal resource/organism + bias). Diagonals invisible."""
    return (
        _present(observation, CellKind.RESOURCE, "N"),
        _present(observation, CellKind.RESOURCE, "S"),
        _present(observation, CellKind.RESOURCE, "E"),
        _present(observation, CellKind.RESOURCE, "W"),
        _present(observation, CellKind.ORGANISM, "N"),
        _present(observation, CellKind.ORGANISM, "S"),
        _present(observation, CellKind.ORGANISM, "E"),
        _present(observation, CellKind.ORGANISM, "W"),
        1.0,
    )


def extract_features_diag(observation: Observation) -> tuple[float, ...]:
    """C2-diag: 17 features — C2 cardinals plus four diagonal resource/organism bits."""
    return (
        _present(observation, CellKind.RESOURCE, "N"),
        _present(observation, CellKind.RESOURCE, "S"),
        _present(observation, CellKind.RESOURCE, "E"),
        _present(observation, CellKind.RESOURCE, "W"),
        _present(observation, CellKind.RESOURCE, "NE"),
        _present(observation, CellKind.RESOURCE, "SE"),
        _present(observation, CellKind.RESOURCE, "SW"),
        _present(observation, CellKind.RESOURCE, "NW"),
        _present(observation, CellKind.ORGANISM, "N"),
        _present(observation, CellKind.ORGANISM, "S"),
        _present(observation, CellKind.ORGANISM, "E"),
        _present(observation, CellKind.ORGANISM, "W"),
        _present(observation, CellKind.ORGANISM, "NE"),
        _present(observation, CellKind.ORGANISM, "SE"),
        _present(observation, CellKind.ORGANISM, "SW"),
        _present(observation, CellKind.ORGANISM, "NW"),
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


def diag_oracle_genome() -> tuple[float, ...]:
    """Hand-set 85 weights for C2-diag features.

    Cardinal resource → that move. Diagonal resource activates both adjacent
    cardinal moves (equal weight), so NE food ties NORTH and EAST.
    Not a fitted C1 clone (distance still collapsed; action space still 5).
    """
    weights = [0.0] * DIAG_N_GENOME_WEIGHTS
    # action indices: N=0 S=1 E=2 W=3 STAY=4
    # feature indices match DIAG_FEATURE_NAMES
    for action_index, feature_index in ((0, 0), (1, 1), (2, 2), (3, 3)):
        weights[action_index * DIAG_N_FEATURES + feature_index] = 1.0
    # NE=4 → N and E; SE=5 → S and E; SW=6 → S and W; NW=7 → N and W
    diagonal_to_actions = {
        4: (0, 2),
        5: (1, 2),
        6: (1, 3),
        7: (0, 3),
    }
    for feature_index, action_indices in diagonal_to_actions.items():
        for action_index in action_indices:
            weights[action_index * DIAG_N_FEATURES + feature_index] = 1.0
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


def _argmax_action(
    rng: random.Random,
    features: tuple[float, ...],
    genome: tuple[float, ...],
    n_features: int,
) -> Action:
    scores: list[float] = []
    for action_index, _action in enumerate(ALL_ACTIONS):
        score = 0.0
        for feature_index, feature in enumerate(features):
            weight = genome[action_index * n_features + feature_index]
            score += weight * feature
        scores.append(score)
    best = max(scores)
    winners = [
        action
        for action, score in zip(ALL_ACTIONS, scores, strict=True)
        if score == best
    ]
    return winners[rng.randrange(len(winners))]


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
        if len(genome) != N_GENOME_WEIGHTS:
            raise ValueError(
                f"C2 genome length {len(genome)} != {N_GENOME_WEIGHTS}; "
                "use evolutionary_diag for 17-feature genomes"
            )
        action = _argmax_action(self.rng, extract_features(observation), genome, N_FEATURES)
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


class EvolutionaryDiagController(Controller):
    """C2-diag: linear policy over 17 features (cardinals + diagonals). Named experiment."""

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
            raise ValueError("evolutionary_diag controller requires a genome")
        if len(genome) != DIAG_N_GENOME_WEIGHTS:
            raise ValueError(
                f"C2-diag genome length {len(genome)} != {DIAG_N_GENOME_WEIGHTS}"
            )
        action = _argmax_action(
            self.rng, extract_features_diag(observation), genome, DIAG_N_FEATURES
        )
        return Decision(action=action)


class EvolutionaryDiagOracleController(EvolutionaryDiagController):
    """Fixed diag-oracle genome over 17 features; no evolution of weights."""

    def decide(
        self,
        observation: Observation,
        *,
        genome: tuple[float, ...] | None = None,
        memory: list[str] | None = None,
    ) -> Decision:
        return super().decide(
            observation,
            genome=diag_oracle_genome(),
            memory=memory,
        )

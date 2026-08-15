"""Shared world primitives."""

from __future__ import annotations

from enum import Enum


class Action(str, Enum):
    MOVE_NORTH = "MOVE_NORTH"
    MOVE_SOUTH = "MOVE_SOUTH"
    MOVE_EAST = "MOVE_EAST"
    MOVE_WEST = "MOVE_WEST"
    STAY = "STAY"


class CellKind(str, Enum):
    EMPTY = "EMPTY"
    RESOURCE = "RESOURCE"
    ORGANISM = "ORGANISM"
    SELF = "SELF"


ALL_ACTIONS: tuple[Action, ...] = (
    Action.MOVE_NORTH,
    Action.MOVE_SOUTH,
    Action.MOVE_EAST,
    Action.MOVE_WEST,
    Action.STAY,
)

# x increases east, y increases north. Torus wrap is applied by the world.
ACTION_DELTA: dict[Action, tuple[int, int]] = {
    Action.MOVE_NORTH: (0, 1),
    Action.MOVE_SOUTH: (0, -1),
    Action.MOVE_EAST: (1, 0),
    Action.MOVE_WEST: (-1, 0),
    Action.STAY: (0, 0),
}

# Birth neighbor scan order: North, East, South, West.
NEIGHBOR_DELTAS: tuple[tuple[int, int], ...] = (
    (0, 1),
    (1, 0),
    (0, -1),
    (-1, 0),
)

N_FEATURES = 9
N_GENOME_WEIGHTS = N_FEATURES * len(ALL_ACTIONS)  # 45
FEATURE_NAMES: tuple[str, ...] = (
    "resource_N",
    "resource_S",
    "resource_E",
    "resource_W",
    "organism_N",
    "organism_S",
    "organism_E",
    "organism_W",
    "bias",
)

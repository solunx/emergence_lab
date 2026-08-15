"""World-state invariants used as model verification, not just unit tests."""

from __future__ import annotations

from emergence_lab.world.world import WorldState


class InvariantError(AssertionError):
    pass


def assert_invariants(state: WorldState) -> None:
    living = [org for org in state.organisms if org.alive]
    dead = [org for org in state.organisms if not org.alive]
    occupied_cells = [(org.x, org.y) for org in living]
    if len(occupied_cells) != len(set(occupied_cells)):
        raise InvariantError("two living organisms occupy the same cell")
    if len(occupied_cells) != len(living):
        raise InvariantError("occupied cell count != living count")
    if set(state.occupied.keys()) != set(occupied_cells):
        raise InvariantError("occupancy index is stale")
    for org in dead:
        if (org.x, org.y) in state.occupied and state.occupied[(org.x, org.y)] == org.id:
            raise InvariantError("dead organism still occupies a cell")
    food_cells = {(site.x, site.y) for site in state.sites if site.has_food}
    if food_cells != state.food:
        raise InvariantError("food index is stale")
    for org in living:
        if (org.x, org.y) in food_cells:
            raise InvariantError("organism and resource occupy the same cell")
    ids = [org.id for org in state.organisms]
    if len(ids) != len(set(ids)):
        raise InvariantError("duplicate organism ids")

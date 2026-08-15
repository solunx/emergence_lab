"""Rebuild world frames from tick-0 snapshot + events. No re-simulation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterator

from emergence_lab.world.organism import Organism
from emergence_lab.world.world import WorldState


def apply_event(state: WorldState, event: dict[str, Any]) -> None:
    kind = event["event"]
    if kind == "MOVE":
        org = state.organism_by_id(event["organism_id"])
        origin = tuple(event["from"])
        dest = tuple(event["to"])
        if org.alive and (org.x, org.y) == origin:
            state.occupied.pop(origin, None)
            org.x, org.y = dest
            state.occupied[dest] = org.id
    elif kind == "RESOURCE_CONSUMED":
        pos = (event["x"], event["y"])
        site = state.site_index[pos]
        site.has_food = False
        site.last_consumed_tick = event["tick"]
        state.food.discard(pos)
        if "organism_id" in event:
            org = state.organism_by_id(event["organism_id"])
            org.energy += event.get("value", state.config.resource_value)
    elif kind == "RESOURCE_REGEN":
        pos = (event["x"], event["y"])
        site = state.site_index[pos]
        site.has_food = True
        state.food.add(pos)
    elif kind == "DEATH":
        org = state.organism_by_id(event["organism_id"])
        org.alive = False
        state.occupied.pop((org.x, org.y), None)
    elif kind == "BIRTH":
        child = Organism(
            id=event["child_id"],
            x=event["x"],
            y=event["y"],
            energy=event.get("child_energy", state.config.reproduction_cost),
            age=0,
            alive=True,
            parent_id=event["parent_id"],
            generation=state.organism_by_id(event["parent_id"]).generation + 1,
            controller_condition=state.organism_by_id(event["parent_id"]).controller_condition,
            genome=None,
            memory=[],
        )
        state.organisms.append(child)
        state.occupied[(child.x, child.y)] = child.id
        state.next_organism_id = max(state.next_organism_id, child.id + 1)
    elif kind == "ACTION":
        return
    elif kind in {
        "OBSERVATION",
        "TICK_STARTED",
        "TICK_FINISHED",
        "MOVE_BLOCKED",
        "MOVE_CONFLICT",
        "INVALID_ACTION",
        "MEMORY_WRITE",
    }:
        return


def clone_state(state: WorldState) -> WorldState:
    return WorldState.from_dict(deepcopy(state.to_dict()))


def iter_tick_states(
    initial: WorldState,
    events: list[dict[str, Any]],
) -> Iterator[tuple[int, WorldState]]:
    state = clone_state(initial)
    yield 0, clone_state(state)
    current_tick: int | None = None
    for event in events:
        if event.get("phase") == "initial":
            continue
        tick = event["tick"]
        if current_tick is None:
            current_tick = tick
        if tick != current_tick:
            yield current_tick + 1, clone_state(state)
            current_tick = tick
        apply_event(state, event)
    if current_tick is not None:
        yield current_tick + 1, clone_state(state)

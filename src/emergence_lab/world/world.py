"""Toroidal grid, occupancy, patches, observations."""

from __future__ import annotations

from dataclasses import dataclass, field

from emergence_lab.config import SimConfig
from emergence_lab.world.observation import Observation
from emergence_lab.world.organism import Organism
from emergence_lab.world.resource import ResourceSite
from emergence_lab.world.types import (
    ACTION_DELTA,
    ALL_ACTIONS,
    N_GENOME_WEIGHTS,
    Action,
    CellKind,
)


def wrap(value: int, size: int) -> int:
    return value % size


@dataclass
class WorldState:
    width: int
    height: int
    tick: int
    seed: int
    organisms: list[Organism]
    sites: list[ResourceSite]
    next_organism_id: int
    config: SimConfig
    occupied: dict[tuple[int, int], int] = field(default_factory=dict)
    food: set[tuple[int, int]] = field(default_factory=set)
    site_index: dict[tuple[int, int], ResourceSite] = field(default_factory=dict)

    def rebuild_indexes(self) -> None:
        self.occupied = {
            (org.x, org.y): org.id for org in self.organisms if org.alive
        }
        self.food = {(site.x, site.y) for site in self.sites if site.has_food}
        self.site_index = {(site.x, site.y): site for site in self.sites}

    def wrap_xy(self, x: int, y: int) -> tuple[int, int]:
        return wrap(x, self.width), wrap(y, self.height)

    def living(self) -> list[Organism]:
        return sorted((org for org in self.organisms if org.alive), key=lambda o: o.id)

    def organism_by_id(self, organism_id: int) -> Organism:
        for org in self.organisms:
            if org.id == organism_id:
                return org
        raise KeyError(organism_id)

    def destination(self, x: int, y: int, action: Action) -> tuple[int, int]:
        dx, dy = ACTION_DELTA[action]
        return self.wrap_xy(x + dx, y + dy)

    def observe(self, organism: Organism) -> Observation:
        radius = self.config.observation_radius
        size = 2 * radius + 1
        rows: list[tuple[CellKind, ...]] = []
        for row in range(size):
            dy = radius - row  # row 0 is north
            cells: list[CellKind] = []
            for col in range(size):
                dx = col - radius  # col 0 is west
                x, y = self.wrap_xy(organism.x + dx, organism.y + dy)
                if dx == 0 and dy == 0:
                    cells.append(CellKind.SELF)
                elif (x, y) in self.occupied:
                    cells.append(CellKind.ORGANISM)
                elif (x, y) in self.food:
                    cells.append(CellKind.RESOURCE)
                else:
                    cells.append(CellKind.EMPTY)
            rows.append(tuple(cells))
        return Observation(
            energy=organism.energy,
            age=organism.age,
            cells=tuple(rows),
            available_actions=ALL_ACTIONS,
        )

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "tick": self.tick,
            "seed": self.seed,
            "next_organism_id": self.next_organism_id,
            "organisms": [org.to_dict() for org in self.organisms],
            "sites": [site.to_dict() for site in self.sites],
            "config": self.config.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> WorldState:
        config = SimConfig(
            **{
                key: value
                for key, value in data["config"].items()
                if key in SimConfig.__dataclass_fields__
            }
        )
        state = cls(
            width=data["width"],
            height=data["height"],
            tick=data["tick"],
            seed=data["seed"],
            organisms=[Organism.from_dict(item) for item in data["organisms"]],
            sites=[ResourceSite.from_dict(item) for item in data["sites"]],
            next_organism_id=data["next_organism_id"],
            config=config,
        )
        state.rebuild_indexes()
        return state


def random_genome(rng) -> tuple[float, ...]:
    return tuple(
        rng.uniform(-0.1, 0.1) for _ in range(N_GENOME_WEIGHTS)
    )


def generate_world(config: SimConfig, world_rng, evolution_rng) -> WorldState:
    cells = [(x, y) for y in range(config.height) for x in range(config.width)]
    if config.resource_count + config.initial_population > len(cells):
        raise ValueError("Not enough cells for sites and organisms")
    site_positions = world_rng.sample(cells, config.resource_count)
    site_set = set(site_positions)
    free = [cell for cell in cells if cell not in site_set]
    organism_positions = world_rng.sample(free, config.initial_population)

    sites = [
        ResourceSite(
            x=x,
            y=y,
            has_food=True,
            last_consumed_tick=-config.regen_delay,
        )
        for x, y in site_positions
    ]
    organisms = []
    for idx, (x, y) in enumerate(organism_positions):
        genome = random_genome(evolution_rng) if config.genome_enabled else None
        organisms.append(
            Organism(
                id=idx,
                x=x,
                y=y,
                energy=config.initial_energy,
                age=0,
                alive=True,
                parent_id=None,
                generation=0,
                controller_condition=config.controller,
                genome=genome,
                memory=[],
            )
        )
    state = WorldState(
        width=config.width,
        height=config.height,
        tick=0,
        seed=config.seed,
        organisms=organisms,
        sites=sites,
        next_organism_id=config.initial_population,
        config=config,
    )
    state.rebuild_indexes()
    return state


def clone_world_for_controller(
    layout: WorldState,
    config: SimConfig,
    evolution_rng,
) -> WorldState:
    """Clone tick-0 occupancy/resources, then attach controller-specific state."""
    cloned_config = SimConfig(**{**config.to_dict(), "controller": config.controller})
    organisms = []
    for org in layout.organisms:
        genome = random_genome(evolution_rng) if cloned_config.genome_enabled else None
        organisms.append(
            Organism(
                id=org.id,
                x=org.x,
                y=org.y,
                energy=org.energy,
                age=org.age,
                alive=org.alive,
                parent_id=org.parent_id,
                generation=org.generation,
                controller_condition=cloned_config.controller,
                genome=genome,
                memory=[],
            )
        )
    sites = [
        ResourceSite(
            x=site.x,
            y=site.y,
            has_food=site.has_food,
            last_consumed_tick=site.last_consumed_tick,
        )
        for site in layout.sites
    ]
    state = WorldState(
        width=layout.width,
        height=layout.height,
        tick=0,
        seed=layout.seed,
        organisms=organisms,
        sites=sites,
        next_organism_id=layout.next_organism_id,
        config=cloned_config,
    )
    state.rebuild_indexes()
    return state

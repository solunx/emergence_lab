from emergence_lab.config import SimConfig
from emergence_lab.controllers.evolutionary import mutate_genome
from emergence_lab.simulation.engine import Engine, make_controller
from emergence_lab.simulation.rng import RNGBundle
from emergence_lab.world.organism import Organism
from emergence_lab.world.resource import ResourceSite
from emergence_lab.world.world import WorldState, random_genome


def _empty_state(**kwargs) -> WorldState:
    params = dict(
        width=8,
        height=8,
        resource_count=0,
        initial_population=0,
        seed=99,
        controller="evolutionary",
        genome_enabled=True,
        reproduction_enabled=True,
        regen_delay=25,
    )
    params.update(kwargs)
    config = SimConfig(**params)
    state = WorldState(
        width=config.width,
        height=config.height,
        tick=0,
        seed=99,
        organisms=[],
        sites=[],
        next_organism_id=0,
        config=config,
    )
    state.rebuild_indexes()
    return state


def test_reproduction_after_metabolism_requires_surplus():
    rng = RNGBundle.from_seed(99)
    state = _empty_state()
    genome = random_genome(rng.evolution)
    parent = Organism(
        id=0,
        x=3,
        y=3,
        energy=160,
        controller_condition="evolutionary",
        genome=genome,
    )
    state.organisms.append(parent)
    state.next_organism_id = 1
    state.rebuild_indexes()
    engine = Engine(state, rng, make_controller("always_stay", rng), check_invariants=True)
    # always_stay with genome_enabled still tries to reproduce
    engine.step(0)
    children = [o for o in state.organisms if o.parent_id == 0]
    assert len(children) == 1
    child = children[0]
    assert child.energy == 75
    assert child.controller_condition == "evolutionary"
    assert parent.energy == 160 - 1 - 75
    assert child.age == 1  # incremented after birth


def test_newborn_consumes_resource_immediately():
    rng = RNGBundle.from_seed(5)
    state = _empty_state()
    genome = random_genome(rng.evolution)
    parent = Organism(
        id=0,
        x=3,
        y=3,
        energy=160,
        controller_condition="evolutionary",
        genome=genome,
    )
    # Force birth cell: AlwaysStay parent, pick_index chooses among empty NESW.
    # Put food on ALL four neighbors so whichever is chosen is a consume.
    state.organisms.append(parent)
    state.next_organism_id = 1
    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        x, y = state.wrap_xy(3 + dx, 3 + dy)
        state.sites.append(ResourceSite(x, y, has_food=True, last_consumed_tick=-25))
    state.rebuild_indexes()
    engine = Engine(state, rng, make_controller("always_stay", rng), check_invariants=True)
    engine.step(0)
    child = next(o for o in state.organisms if o.parent_id == 0)
    assert child.energy == 75 + state.config.resource_value
    assert child.position not in state.food


def test_no_birth_without_free_neighbor():
    rng = RNGBundle.from_seed(6)
    state = _empty_state()
    state.width = 1
    state.height = 1
    state.config.width = 1
    state.config.height = 1
    genome = random_genome(rng.evolution)
    parent = Organism(
        id=0, x=0, y=0, energy=200, controller_condition="evolutionary", genome=genome
    )
    state.organisms.append(parent)
    state.next_organism_id = 1
    state.rebuild_indexes()
    engine = Engine(state, rng, make_controller("always_stay", rng), check_invariants=True)
    engine.step(0)
    assert len(state.organisms) == 1
    assert parent.energy == 199  # metabolism only


def test_regen_delay_timing():
    rng = RNGBundle.from_seed(8)
    state = _empty_state(
        controller="always_north",
        genome_enabled=False,
        reproduction_enabled=False,
        width=8,
        height=32,
    )
    org = Organism(id=0, x=2, y=2, energy=100, controller_condition="always_north")
    site = ResourceSite(2, 3, has_food=True, last_consumed_tick=-25)
    state.organisms.append(org)
    state.sites.append(site)
    state.next_organism_id = 1
    state.rebuild_indexes()
    engine = Engine(state, rng, make_controller("always_north", rng), check_invariants=True)
    engine.step(0)  # moves north onto food, consumes, last_consumed=0
    assert not site.has_food
    consumed_tick = site.last_consumed_tick
    assert consumed_tick == 0
    for t in range(1, 25):
        engine.step(t)
        assert site.has_food is False
    engine.step(25)
    assert site.has_food is True


def test_no_regen_under_organism():
    rng = RNGBundle.from_seed(9)
    state = _empty_state(controller="always_stay", genome_enabled=False, reproduction_enabled=False)
    state.config.genome_enabled = False
    state.config.reproduction_enabled = False
    org = Organism(id=0, x=4, y=4, energy=100, controller_condition="always_stay")
    site = ResourceSite(4, 4, has_food=False, last_consumed_tick=-25)
    state.organisms.append(org)
    state.sites.append(site)
    state.next_organism_id = 1
    state.rebuild_indexes()
    engine = Engine(state, rng, make_controller("always_stay", rng), check_invariants=True)
    engine.step(0)
    assert site.has_food is False


def test_mutate_genome_length():
    rng = RNGBundle.from_seed(1)
    genome = random_genome(rng.evolution)
    child = mutate_genome(genome, rng.evolution, 1.0, 0.1)
    assert len(child) == len(genome)
    assert child != genome

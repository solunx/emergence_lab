from emergence_lab.config import SimConfig
from emergence_lab.simulation.engine import Engine, make_controller
from emergence_lab.simulation.rng import RNGBundle, conflict_winner
from emergence_lab.world.invariants import assert_invariants
from emergence_lab.world.types import CellKind
from emergence_lab.world.world import WorldState, generate_world


def tiny_config(**kwargs) -> SimConfig:
    base = dict(
        width=8,
        height=8,
        resource_count=3,
        initial_population=3,
        ticks=20,
        seed=1,
        controller="random",
        regen_delay=25,
    )
    base.update(kwargs)
    return SimConfig(**base)


def test_torus_wrap():
    config = tiny_config()
    rng = RNGBundle.from_seed(1)
    state = generate_world(config, rng.world, rng.evolution)
    x, y = state.wrap_xy(-1, 8)
    assert x == 7
    assert y == 0


def test_initial_placement_no_overlap_or_food_spawn():
    config = tiny_config(width=16, height=16, resource_count=8, initial_population=8)
    rng = RNGBundle.from_seed(42)
    state = generate_world(config, rng.world, rng.evolution)
    positions = [(o.x, o.y) for o in state.living()]
    assert len(positions) == len(set(positions))
    site_pos = {(s.x, s.y) for s in state.sites}
    assert len(site_pos) == 8
    for pos in positions:
        assert pos not in site_pos
    assert_invariants(state)


def test_observation_center_is_self_and_egocentric():
    config = tiny_config(resource_count=1, initial_population=1)
    rng = RNGBundle.from_seed(7)
    state = generate_world(config, rng.world, rng.evolution)
    org = state.living()[0]
    obs = state.observe(org)
    assert obs.cells[2][2] is CellKind.SELF
    assert org.energy == obs.energy
    # No global coordinates leaked.
    dumped = obs.to_dict()
    assert "x" not in dumped
    assert "position" not in dumped


def test_observation_sees_northern_resource():
    config = tiny_config(resource_count=0, initial_population=1, observation_radius=2)
    rng = RNGBundle.from_seed(1)
    state = generate_world(config, rng.world, rng.evolution)
    org = state.living()[0]
    from emergence_lab.world.resource import ResourceSite

    nx, ny = state.wrap_xy(org.x, org.y + 1)
    site = ResourceSite(nx, ny, has_food=True, last_consumed_tick=-25)
    state.sites.append(site)
    state.rebuild_indexes()
    obs = state.observe(org)
    assert obs.cells[1][2] is CellKind.RESOURCE  # one cell north


def test_conflict_hash_is_stable_and_not_python_hash():
    ids = [9, 3, 4]
    a = conflict_winner(123, 10, 5, 6, ids)
    b = conflict_winner(123, 10, 5, 6, list(reversed(ids)))
    assert a == b
    assert a in sorted(ids)


def test_stay_and_move_energy_and_death():
    config = tiny_config(
        controller="always_stay",
        initial_population=1,
        resource_count=0,
        initial_energy=5,
    )
    rng = RNGBundle.from_seed(2)
    state = generate_world(config, rng.world, rng.evolution)
    engine = Engine(state, rng, make_controller("always_stay", rng), check_invariants=True)
    engine.run(5)
    living = state.living()
    assert living == []
    assert engine.deaths == 1


def test_move_costs_two():
    config = tiny_config(
        controller="always_north",
        initial_population=1,
        resource_count=0,
        initial_energy=10,
    )
    rng = RNGBundle.from_seed(3)
    state = generate_world(config, rng.world, rng.evolution)
    engine = Engine(state, rng, make_controller("always_north", rng), check_invariants=True)
    engine.run(1)
    org = [o for o in state.organisms if o.id == 0][0]
    assert org.energy == 8  # 10 - 2
    assert org.alive


def test_always_north_wraps_torus():
    config = tiny_config(
        controller="always_north",
        width=5,
        height=5,
        initial_population=1,
        resource_count=0,
        initial_energy=100,
    )
    rng = RNGBundle.from_seed(4)
    state = generate_world(config, rng.world, rng.evolution)
    y0 = state.living()[0].y
    engine = Engine(state, rng, make_controller("always_north", rng), check_invariants=True)
    engine.run(5)
    org = state.living()[0]
    assert org.y == y0
    assert org.x == state.organisms[0].x

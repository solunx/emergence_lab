from emergence_lab.config import SimConfig
from emergence_lab.simulation.engine import Engine, make_controller
from emergence_lab.simulation.events import EventLog
from emergence_lab.simulation.rng import RNGBundle
from emergence_lab.simulation.runner import generate_layout, run_simulation, world_for_controller
from emergence_lab.world.invariants import assert_invariants
from emergence_lab.world.world import generate_world


def test_same_seed_identical_event_hash(tmp_path):
    config = SimConfig(
        width=12,
        height=12,
        resource_count=6,
        initial_population=5,
        ticks=40,
        seed=123,
        controller="random",
        experiment_id="repro",
    )
    hashes = []
    for _ in range(2):
        out = tmp_path / f"run_{len(hashes)}"
        run_simulation(config, out, check_invariants=True)
        log = EventLog()
        # load written file hash from metadata
        import json

        meta = json.loads((out / "metadata.json").read_text())
        hashes.append(meta["event_log_sha256"])
    assert hashes[0] == hashes[1]


def test_same_world_clones_share_tick0_positions(tmp_path):
    config = SimConfig(
        width=12,
        height=12,
        resource_count=6,
        initial_population=5,
        ticks=5,
        seed=77,
        controller="random",
    )
    layout = generate_layout(config)
    pos = {(o.id, o.x, o.y) for o in layout.living()}
    sites = {(s.x, s.y) for s in layout.sites}
    for name in ("random", "reactive", "evolutionary"):
        cfg = SimConfig(
            width=12,
            height=12,
            resource_count=6,
            initial_population=5,
            ticks=5,
            seed=77,
            controller=name,
        )
        cfg.__post_init__()
        cloned = world_for_controller(layout, cfg)
        assert {(o.id, o.x, o.y) for o in cloned.living()} == pos
        assert {(s.x, s.y) for s in cloned.sites} == sites
        if name == "evolutionary":
            assert all(o.genome is not None for o in cloned.living())
        else:
            assert all(o.genome is None for o in cloned.living())


def test_invariants_hold_for_c0_c1_c2():
    for name in ("random", "reactive", "evolutionary"):
        config = SimConfig(
            width=10,
            height=10,
            resource_count=5,
            initial_population=4,
            ticks=30,
            seed=11,
            controller=name,
        )
        rng = RNGBundle.from_seed(11)
        state = generate_world(config, rng.world, rng.evolution)
        engine = Engine(state, rng, make_controller(name, rng), check_invariants=True)
        engine.run(30)
        assert_invariants(state)


def test_decisions_use_state_t_not_moved_neighbors():
    """Two stacked organisms both move north; each must see the other before movement."""
    from emergence_lab.world.organism import Organism
    from emergence_lab.world.types import CellKind
    from emergence_lab.world.world import WorldState

    config = SimConfig(
        width=8,
        height=8,
        resource_count=0,
        initial_population=0,
        seed=1,
        controller="always_north",
        genome_enabled=False,
        reproduction_enabled=False,
    )
    state = WorldState(
        width=8,
        height=8,
        tick=0,
        seed=1,
        organisms=[
            Organism(id=0, x=3, y=3, energy=50, controller_condition="always_north"),
            Organism(id=1, x=3, y=4, energy=50, controller_condition="always_north"),
        ],
        sites=[],
        next_organism_id=2,
        config=config,
    )
    state.rebuild_indexes()
    rng = RNGBundle.from_seed(1)
    engine = Engine(state, rng, make_controller("always_north", rng), check_invariants=True)
    obs0 = state.observe(state.organism_by_id(0))
    obs1 = state.observe(state.organism_by_id(1))
    # id0 looks north (row 1, col 2) and should see id1
    assert obs0.cells[1][2] is CellKind.ORGANISM
    # id1 looks south (row 3, col 2) and should see id0
    assert obs1.cells[3][2] is CellKind.ORGANISM
    engine.step(0)
    # Destination (3,4) is occupied at T, so id0 cannot follow into the hole.
    a = state.organism_by_id(0)
    b = state.organism_by_id(1)
    assert (a.x, a.y) == (3, 3)
    assert (b.x, b.y) == (3, 5)

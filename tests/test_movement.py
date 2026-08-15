from emergence_lab.config import SimConfig
from emergence_lab.simulation.engine import Engine, make_controller
from emergence_lab.simulation.rng import RNGBundle
from emergence_lab.world.organism import Organism
from emergence_lab.world.world import WorldState


def test_move_conflict_one_winner_other_stays():
    config = SimConfig(
        width=8,
        height=8,
        resource_count=0,
        initial_population=0,
        seed=42,
        controller="always_north",
        genome_enabled=False,
        reproduction_enabled=False,
        initial_energy=50,
    )
    # Two organisms both target (4,5): one from (4,4) going north, one from (4,6)
    # going south. Use a custom controller mix by setting intended via two always_*
    # That's awkward. Instead: both AlwaysNorth from (3,4) and (5,4) cannot conflict.
    # Conflict: A at (4,4) AlwaysNorth, B at (4,4) impossible.
    # A at (4,3) north->(4,4), B at (5,4) west->(4,4). Need two different controllers.
    # Engine has one controller for all. So give both AlwaysNorth and place them
    # so they claim the same empty cell: A (4,4) north (4,5), B (4,6) cannot go south.
    #
    # Both go north: A (4,4)->(4,5), B (3,5)->(3,6) no conflict.
    # Same target: A (4,4)->(4,5), B (4,4) duplicate.
    # A at (4,4) north to (4,5); B at (5,5) west - not always north.
    #
    # Use random? Non-deterministic.
    # Simplest: subclass via always_north from cells that both map north to same
    # torus collision: A (0, 7) north -> (0, 0) wait height 8, y=7 north -> y=0.
    # B at (0, 0) stay wouldn't.
    # A (1,4) and B (0,4) both north -> (1,5) and (0,5), different.
    #
    # Two agents east and west of a cell both moving toward it needs different actions.
    # Engine uses one controller. For conflict test, patch intended by using
    # organisms that wrap: 
    # Actually put A at (4,4), B at (4,4) is invalid.
    #
    # I'll use AlwaysNorth on a 2-wide mapping... skip dual-action.
    # Place A at (4,4) and B at (4,4+height) impossible.
    #
    # Direct unit test of _resolve_movement instead.
    state = WorldState(
        width=8,
        height=8,
        tick=0,
        seed=42,
        organisms=[
            Organism(id=0, x=4, y=4, energy=50),
            Organism(id=1, x=4, y=6, energy=50),
        ],
        sites=[],
        next_organism_id=2,
        config=config,
    )
    state.rebuild_indexes()
    rng = RNGBundle.from_seed(42)
    engine = Engine(state, rng, make_controller("always_stay", rng))
    intended = {0: (4, 5), 1: (4, 5)}
    winners, blocked = engine._resolve_movement(
        0, state.living(), intended, {(4, 4), (4, 6)}
    )
    assert len(winners) == 1
    assert len(blocked) == 1
    assert winners.isdisjoint(blocked)
    kinds = [e.kind for e in engine.log.events]
    assert "MOVE_CONFLICT" in kinds


def test_cannot_enter_cell_occupied_at_start_even_if_occupant_leaves():
    config = SimConfig(
        width=8,
        height=8,
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
            Organism(id=0, x=2, y=2, energy=50, controller_condition="always_north"),
            Organism(id=1, x=2, y=3, energy=50, controller_condition="always_north"),
        ],
        sites=[],
        next_organism_id=2,
        config=config,
    )
    state.rebuild_indexes()
    rng = RNGBundle.from_seed(1)
    engine = Engine(state, rng, make_controller("always_north", rng), check_invariants=True)
    engine.step(0)
    a = state.organism_by_id(0)
    b = state.organism_by_id(1)
    # Occupant at (2,3) left to (2,4); follower at (2,2) cannot enter (2,3).
    assert (a.x, a.y) == (2, 2)
    assert (b.x, b.y) == (2, 4)
    blocked = [e for e in engine.log.events if e.kind == "MOVE_BLOCKED"]
    assert blocked

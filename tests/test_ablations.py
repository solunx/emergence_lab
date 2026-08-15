from emergence_lab.config import SimConfig
from emergence_lab.controllers.reactive import ReactiveController
from emergence_lab.simulation.engine import Engine, make_controller
from emergence_lab.simulation.events import EventLog
from emergence_lab.simulation.rng import RNGBundle
from emergence_lab.simulation.runner import run_simulation
from emergence_lab.world.organism import Organism
from emergence_lab.world.world import WorldState


def test_reactive_r_flags_and_decision_class():
    cfg = SimConfig(controller="reactive_r")
    assert cfg.reproduction_enabled is True
    assert cfg.genome_enabled is False
    cfg_c1 = SimConfig(controller="reactive")
    assert cfg_c1.reproduction_enabled is False
    rng = RNGBundle.from_seed(1)
    assert isinstance(make_controller("reactive_r", rng), ReactiveController)


def test_random_r_flags():
    cfg = SimConfig(controller="random_r")
    assert cfg.reproduction_enabled is True
    assert cfg.genome_enabled is False


def test_reactive_r_child_has_no_genome_and_inherits_condition():
    config = SimConfig(
        width=8,
        height=8,
        resource_count=0,
        initial_population=0,
        seed=99,
        controller="reactive_r",
        regen_delay=15,
    )
    state = WorldState(
        width=8,
        height=8,
        tick=0,
        seed=99,
        organisms=[],
        sites=[],
        next_organism_id=0,
        config=config,
    )
    parent = Organism(
        id=0,
        x=3,
        y=3,
        energy=160,
        controller_condition="reactive_r",
        genome=None,
    )
    state.organisms.append(parent)
    state.next_organism_id = 1
    state.rebuild_indexes()
    rng = RNGBundle.from_seed(99)
    engine = Engine(state, rng, make_controller("reactive_r", rng), check_invariants=True)
    engine.step(0)
    children = [org for org in state.organisms if org.parent_id == 0]
    assert len(children) == 1
    child = children[0]
    assert child.genome is None
    assert child.controller_condition == "reactive_r"
    assert child.generation == 1
    assert parent.energy == 160 - 1 - 75 or parent.energy == 160 - 2 - 75


def test_c1_and_c1r_match_when_nobody_reproduces(tmp_path):
    shared = dict(
        width=8,
        height=8,
        resource_count=0,
        initial_population=3,
        ticks=15,
        seed=42,
        initial_energy=20,
        experiment_id="ablation-identity",
    )
    hashes = []
    for name in ("reactive", "reactive_r"):
        out = tmp_path / name
        run_simulation(SimConfig(controller=name, **shared), out, check_invariants=True)
        import json

        hashes.append(json.loads((out / "metadata.json").read_text())["event_log_sha256"])
        births = sum(
            1
            for line in (out / "events.jsonl").read_text().splitlines()
            if '"BIRTH"' in line or '"event": "BIRTH"' in line
        )
        assert births == 0
    assert hashes[0] == hashes[1]

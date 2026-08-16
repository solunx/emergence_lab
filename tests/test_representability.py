import random

from emergence_lab.analytics.representability import (
    agreement_table,
    make_patch,
    resource_visibility,
    single_food_offsets,
)
from emergence_lab.config import SimConfig
from emergence_lab.controllers.evolutionary import (
    EvolutionaryOracleController,
    cardinal_oracle_genome,
    extract_features,
)
from emergence_lab.controllers.reactive import ReactiveController
from emergence_lab.simulation.engine import make_controller
from emergence_lab.simulation.rng import RNGBundle
from emergence_lab.world.types import Action, N_GENOME_WEIGHTS


def test_diagonal_food_is_invisible_to_c2_features():
    obs = make_patch((-1, 1))
    assert resource_visibility(obs) == "diagonal_only"
    assert extract_features(obs)[:4] == (0.0, 0.0, 0.0, 0.0)
    empty = extract_features(make_patch())[:4]
    assert extract_features(obs)[:4] == empty


def test_cardinal_food_sets_the_matching_ray():
    north = extract_features(make_patch((-1, 0)))
    assert north[0] == 1.0
    assert resource_visibility(make_patch((-1, 0))) == "on_axis"
    assert resource_visibility(make_patch((-2, 0))) == "on_axis"


def test_oracle_walks_north_when_food_is_due_north():
    rng = random.Random(0)
    oracle = EvolutionaryOracleController(rng)
    c1 = ReactiveController(random.Random(1))
    obs = make_patch((-1, 0))
    for _ in range(10):
        assert oracle.decide(obs).action is Action.MOVE_NORTH
        assert c1.decide(obs).action is Action.MOVE_NORTH


def test_oracle_genome_size_and_flags():
    assert len(cardinal_oracle_genome()) == N_GENOME_WEIGHTS
    cfg = SimConfig(controller="evolutionary_oracle")
    assert cfg.reproduction_enabled is False
    assert cfg.genome_enabled is False
    cfg_r = SimConfig(controller="evolutionary_oracle_r")
    assert cfg_r.reproduction_enabled is True
    assert cfg_r.genome_enabled is False
    rng = RNGBundle.from_seed(1)
    assert isinstance(make_controller("evolutionary_oracle_r", rng), EvolutionaryOracleController)


def test_agreement_on_axis_high_diagonal_near_chance():
    table = agreement_table(repeats=30, rng_seed=7)
    assert table["on_axis"]["agreement"] >= 0.9
    assert table["diagonal_only"]["agreement"] < 0.45
    assert len(single_food_offsets()) == 24

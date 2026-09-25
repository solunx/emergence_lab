import random

from emergence_lab.analytics.representability import make_patch
from emergence_lab.config import SimConfig
from emergence_lab.controllers.evolutionary import (
    EvolutionaryDiagController,
    EvolutionaryDiagOracleController,
    diag_oracle_genome,
    extract_features,
    extract_features_diag,
)
from emergence_lab.simulation.engine import make_controller
from emergence_lab.simulation.rng import RNGBundle
from emergence_lab.world.types import (
    DIAG_N_FEATURES,
    DIAG_N_GENOME_WEIGHTS,
    N_GENOME_WEIGHTS,
    Action,
)
from emergence_lab.world.world import genome_weight_count, random_genome


def test_diag_features_see_diagonal_food():
    obs = make_patch((-1, 1))
    assert extract_features(obs)[:4] == (0.0, 0.0, 0.0, 0.0)
    diag = extract_features_diag(obs)
    assert len(diag) == DIAG_N_FEATURES
    # resource_NE is index 4
    assert diag[4] == 1.0
    assert diag[:4] == (0.0, 0.0, 0.0, 0.0)


def test_diag_features_keep_cardinal_bits():
    north = extract_features_diag(make_patch((-1, 0)))
    assert north[0] == 1.0
    assert north[4:8] == (0.0, 0.0, 0.0, 0.0)


def test_diag_oracle_ties_north_and_east_on_ne_food():
    rng = random.Random(0)
    oracle = EvolutionaryDiagOracleController(rng)
    obs = make_patch((-1, 1))
    actions = {oracle.decide(obs).action for _ in range(40)}
    assert actions <= {Action.MOVE_NORTH, Action.MOVE_EAST}
    assert Action.MOVE_NORTH in actions
    assert Action.MOVE_EAST in actions


def test_diag_oracle_walks_north_on_cardinal_food():
    rng = random.Random(0)
    oracle = EvolutionaryDiagOracleController(rng)
    obs = make_patch((-1, 0))
    for _ in range(10):
        assert oracle.decide(obs).action is Action.MOVE_NORTH


def test_diag_genome_size_and_controller_flags():
    assert len(diag_oracle_genome()) == DIAG_N_GENOME_WEIGHTS
    assert genome_weight_count("evolutionary") == N_GENOME_WEIGHTS
    assert genome_weight_count("evolutionary_diag") == DIAG_N_GENOME_WEIGHTS
    assert len(random_genome(random.Random(0), DIAG_N_GENOME_WEIGHTS)) == DIAG_N_GENOME_WEIGHTS

    cfg = SimConfig(controller="evolutionary_diag")
    assert cfg.reproduction_enabled is True
    assert cfg.genome_enabled is True
    cfg_o = SimConfig(controller="evolutionary_diag_oracle")
    assert cfg_o.reproduction_enabled is False
    assert cfg_o.genome_enabled is False
    cfg_or = SimConfig(controller="evolutionary_diag_oracle_r")
    assert cfg_or.reproduction_enabled is True
    assert cfg_or.genome_enabled is False

    rng = RNGBundle.from_seed(1)
    assert isinstance(make_controller("evolutionary_diag", rng), EvolutionaryDiagController)
    assert isinstance(
        make_controller("evolutionary_diag_oracle_r", rng), EvolutionaryDiagOracleController
    )


def test_c2_controller_rejects_diag_genome_length():
    rng = random.Random(0)
    ctrl = EvolutionaryDiagController(rng)
    short = tuple(0.0 for _ in range(N_GENOME_WEIGHTS))
    try:
        ctrl.decide(make_patch((-1, 0)), genome=short)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert str(DIAG_N_GENOME_WEIGHTS) in str(exc)

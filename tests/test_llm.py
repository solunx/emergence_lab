from pathlib import Path

from emergence_lab.config import SimConfig
from emergence_lab.controllers.llm import LlmController
from emergence_lab.llm.ollama import FakeLlmClient
from emergence_lab.llm.parse import parse_action
from emergence_lab.llm.prompts import prompt_text
from emergence_lab.simulation.engine import Engine, make_controller
from emergence_lab.simulation.rng import RNGBundle
from emergence_lab.world.types import Action
from emergence_lab.world.world import generate_world


def test_parse_action_tokens():
    assert parse_action("NORTH") is Action.MOVE_NORTH
    assert parse_action("I choose STAY.") is Action.STAY
    assert parse_action("MOVE_EAST") is Action.MOVE_EAST
    assert parse_action("garbage") is None
    assert parse_action("") is None


def test_parse_strips_think_and_uses_last_token():
    raw = "<think>maybe SOUTH</think>\nNORTH"
    assert parse_action(raw) is Action.MOVE_NORTH
    assert parse_action("NORTH\nwait WEST") is Action.MOVE_WEST


def test_prompt_a_has_no_survival_instruction():
    text = prompt_text("llm_a", "GRID")
    assert "NORTH, SOUTH, EAST, WEST, STAY" in text
    assert "remain alive" not in text.lower()
    assert "food" not in text.lower()


def test_prompt_b_is_survival_ablation():
    text = prompt_text("llm_b", "GRID")
    assert "remain alive as long as possible" in text.lower()


def test_llm_a_and_llm_b_flags():
    a = SimConfig(controller="llm_a")
    assert a.reproduction_enabled is False
    assert a.genome_enabled is False
    assert a.llm_prompt_id == "llm_a"
    b = SimConfig(controller="llm_b")
    assert b.llm_prompt_id == "llm_b"
    generic = SimConfig(controller="llm", llm_prompt_id="llm_b")
    assert generic.llm_prompt_id == "llm_b"


def test_fake_llm_north_and_invalid_fallback():
    config = SimConfig(
        width=8,
        height=8,
        resource_count=2,
        initial_population=1,
        ticks=2,
        seed=1,
        controller="llm",
        llm_model="fake",
        regen_delay=15,
    )
    rng = RNGBundle.from_seed(1)
    state = generate_world(config, rng.world, rng.evolution)
    client = FakeLlmClient(["NORTH", "NOPE I refuse"])
    engine = Engine(state, rng, LlmController(config, client=client), check_invariants=True)
    engine.step(0)
    engine.step(1)
    kinds = [event.kind for event in engine.log.events]
    assert kinds.count("LLM_CALL") == 2
    assert "INVALID_ACTION" in kinds
    actions = [e.payload["action"] for e in engine.log.events if e.kind == "ACTION"]
    assert actions[0] == "MOVE_NORTH"
    assert actions[1] == "STAY"
    traces = [e for e in engine.log.events if e.kind == "LLM_CALL"]
    assert traces[0].payload["valid"] is True
    assert traces[1].payload["valid"] is False
    assert traces[1].payload["fallback"] == "STAY"
    assert traces[1].payload["raw_output"] == "NOPE I refuse"
    assert "Choose exactly one valid action" in traces[0].payload["prompt"]
    assert traces[0].payload["model"] == "fake"


def test_yaml_llm_block_is_not_hardcoded():
    root = Path(__file__).resolve().parents[1]
    cfg = SimConfig.from_yaml(root / "experiments" / "configs" / "c3_ollama.yaml")
    assert cfg.controller == "llm"
    assert cfg.llm_model is None
    assert cfg.llm_prompt_id == "llm_a"
    assert "11434" in cfg.llm_endpoint
    cfg.llm_model = "qwen2.5:7b"
    assert cfg.llm_model == "qwen2.5:7b"


def test_make_controller_llm_requires_config():
    rng = RNGBundle.from_seed(1)
    try:
        make_controller("llm", rng)
    except ValueError as exc:
        assert "SimConfig" in str(exc)
    else:
        raise AssertionError("expected ValueError")
    cfg = SimConfig(controller="llm", llm_model="fake")
    controller = make_controller("llm_b", rng, cfg)
    assert isinstance(controller, LlmController)
    assert controller.prompt_id == "llm_b"

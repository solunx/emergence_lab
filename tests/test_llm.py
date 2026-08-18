from pathlib import Path

from emergence_lab.config import SimConfig
from emergence_lab.controllers.llm import LlmController
from emergence_lab.llm.ollama import FakeLlmClient
from emergence_lab.llm.parse import parse_action, parse_llm_output
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
    assert a.memory_enabled is False
    assert a.llm_prompt_id == "llm_a"
    b = SimConfig(controller="llm_b")
    assert b.llm_prompt_id == "llm_b"
    generic = SimConfig(controller="llm", llm_prompt_id="llm_b")
    assert generic.llm_prompt_id == "llm_b"


def test_c4_flags_and_prompt_mapping():
    mem = SimConfig(controller="llm_memory")
    assert mem.memory_enabled is True
    assert mem.reproduction_enabled is False
    assert mem.genome_enabled is False
    assert mem.llm_prompt_id == "llm_a_memory"
    b = SimConfig(controller="llm_b_memory")
    assert b.llm_prompt_id == "llm_b_memory"
    coerced = SimConfig(controller="llm_memory", llm_prompt_id="llm_b")
    assert coerced.llm_prompt_id == "llm_b_memory"
    c3 = SimConfig(controller="llm")
    assert c3.memory_enabled is False
    assert c3.llm_prompt_id == "llm_a"


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
    assert "Memory:" not in traces[0].payload["prompt"]


def test_yaml_llm_block_is_not_hardcoded():
    root = Path(__file__).resolve().parents[1]
    cfg = SimConfig.from_yaml(root / "experiments" / "configs" / "c3_ollama.yaml")
    assert cfg.controller == "llm"
    assert cfg.llm_model is None
    assert cfg.llm_prompt_id == "llm_a"
    assert "11434" in cfg.llm_endpoint
    cfg.llm_model = "qwen2.5:7b"
    assert cfg.llm_model == "qwen2.5:7b"


def test_yaml_c4_block():
    root = Path(__file__).resolve().parents[1]
    cfg = SimConfig.from_yaml(root / "experiments" / "configs" / "c4_ollama.yaml")
    assert cfg.controller == "llm_memory"
    assert cfg.memory_enabled is True
    assert cfg.llm_prompt_id == "llm_a_memory"
    assert cfg.llm_num_predict == 128
    assert cfg.llm_model is None


def test_parse_memory_does_not_steal_action():
    parsed = parse_llm_output("EAST\nMEMORY: last move was WEST, then STAY")
    assert parsed.action is Action.MOVE_EAST
    assert parsed.memory_write == "last move was WEST, then STAY"
    empty = parse_llm_output("NORTH\nMEMORY:")
    assert empty.action is Action.MOVE_NORTH
    assert empty.memory_write is None
    only_mem = parse_llm_output("MEMORY: note")
    assert only_mem.action is None
    assert only_mem.memory_write == "note"


def test_c4_memory_write_visible_next_tick():
    config = SimConfig(
        width=8,
        height=8,
        resource_count=0,
        initial_population=1,
        ticks=2,
        seed=1,
        controller="llm_memory",
        llm_model="fake",
        regen_delay=15,
    )
    rng = RNGBundle.from_seed(1)
    state = generate_world(config, rng.world, rng.evolution)
    client = FakeLlmClient(["STAY\nMEMORY: note-0", "STAY"])
    engine = Engine(state, rng, LlmController(config, client=client), check_invariants=True)
    engine.step(0)
    org = state.living()[0]
    assert org.memory == ["note-0"]
    assert "Memory:\n(empty)" in client.prompts[0]
    assert "note-0" not in client.prompts[0]
    engine.step(1)
    assert "note-0" in client.prompts[1]
    writes = [e for e in engine.log.events if e.kind == "MEMORY_WRITE"]
    assert len(writes) == 1
    assert writes[0].payload["text"] == "note-0"
    assert writes[0].tick == 0


def test_c4_invalid_action_still_writes_memory():
    config = SimConfig(
        width=8,
        height=8,
        resource_count=0,
        initial_population=1,
        ticks=1,
        seed=1,
        controller="llm_a_memory",
        llm_model="fake",
        regen_delay=15,
    )
    rng = RNGBundle.from_seed(1)
    state = generate_world(config, rng.world, rng.evolution)
    client = FakeLlmClient(["NOPE\nMEMORY: keep this"])
    engine = Engine(state, rng, LlmController(config, client=client), check_invariants=True)
    engine.step(0)
    kinds = [event.kind for event in engine.log.events]
    assert "INVALID_ACTION" in kinds
    assert state.living()[0].memory == ["keep this"]


def test_c4_memory_fifo_and_truncation():
    config = SimConfig(
        width=8,
        height=8,
        resource_count=0,
        initial_population=1,
        ticks=3,
        seed=1,
        controller="llm_memory",
        llm_model="fake",
        regen_delay=15,
        memory_capacity=2,
        memory_entry_max_chars=8,
    )
    rng = RNGBundle.from_seed(1)
    state = generate_world(config, rng.world, rng.evolution)
    client = FakeLlmClient(
        [
            "STAY\nMEMORY: abcdefghij",
            "STAY\nMEMORY: second",
            "STAY\nMEMORY: third",
        ]
    )
    engine = Engine(state, rng, LlmController(config, client=client), check_invariants=True)
    engine.step(0)
    engine.step(1)
    engine.step(2)
    assert state.living()[0].memory == ["second", "third"]


def test_c3_ignores_memory_line_in_output():
    config = SimConfig(
        width=8,
        height=8,
        resource_count=0,
        initial_population=1,
        ticks=1,
        seed=1,
        controller="llm",
        llm_model="fake",
        regen_delay=15,
    )
    rng = RNGBundle.from_seed(1)
    state = generate_world(config, rng.world, rng.evolution)
    client = FakeLlmClient(["EAST\nMEMORY: should not persist"])
    engine = Engine(state, rng, LlmController(config, client=client), check_invariants=True)
    engine.step(0)
    assert state.living()[0].memory == []
    assert all(e.kind != "MEMORY_WRITE" for e in engine.log.events)


def test_c4_prompts_are_a_b_plus_memory():
    a = prompt_text("llm_a_memory", "GRID", memory=None)
    b = prompt_text("llm_b_memory", "GRID", memory=["old"])
    assert "remain alive" not in a.lower()
    assert "food" not in a.lower()
    assert "MEMORY:" in a
    assert "(empty)" in a
    assert "remain alive as long as possible" in b.lower()
    assert "- old" in b
    assert prompt_text("llm_a", "GRID").count("Observation:") == 1
    assert "{memory}" not in prompt_text("llm_a", "GRID")


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
    mem = make_controller("llm_memory", rng, SimConfig(controller="llm", llm_model="fake"))
    assert mem.prompt_id == "llm_a_memory"
    assert mem.config.memory_enabled is True

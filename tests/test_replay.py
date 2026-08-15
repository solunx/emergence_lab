import json
from pathlib import Path

from emergence_lab.config import SimConfig
from emergence_lab.simulation.events import read_events
from emergence_lab.simulation.replay import iter_tick_states
from emergence_lab.simulation.runner import run_simulation
from emergence_lab.simulation.snapshots import read_snapshot
from emergence_lab.visualization.gif import gif_from_run


def test_replay_matches_final_occupancy(tmp_path):
    config = SimConfig(
        width=10,
        height=10,
        resource_count=5,
        initial_population=4,
        ticks=25,
        seed=21,
        controller="reactive",
        experiment_id="replay",
    )
    out = tmp_path / "run"
    run_simulation(config, out, check_invariants=True)
    initial = read_snapshot(out / "snapshots" / "tick_000000.json")
    events = read_events(out / "events.jsonl")
    frames = list(iter_tick_states(initial, events))
    final_state = frames[-1][1]
    recorded = read_snapshot(out / "snapshots" / "tick_000025.json")
    live = {(o.id, o.x, o.y) for o in recorded.living()}
    replayed = {(o.id, o.x, o.y) for o in final_state.living()}
    assert live == replayed


def test_gif_from_stored_run_without_resimulating(tmp_path):
    config = SimConfig(
        width=8,
        height=8,
        resource_count=3,
        initial_population=3,
        ticks=12,
        seed=3,
        controller="random",
    )
    out = tmp_path / "run"
    run_simulation(config, out)
    gif_path = gif_from_run(out, tmp_path / "out.gif", max_frames=20)
    assert gif_path.exists()
    assert gif_path.stat().st_size > 0
    kinds = {e["event"] for e in read_events(out / "events.jsonl")}
    assert "MOVE" in kinds or "TICK_FINISHED" in kinds


def test_comparison_gif_has_gutters_and_is_wider_than_one_panel(tmp_path):
    from emergence_lab.visualization.gif import comparison_gif
    from emergence_lab.visualization.renderer import render_image

    paths = {}
    for name in ("random", "reactive"):
        config = SimConfig(
            width=8,
            height=8,
            resource_count=2,
            initial_population=2,
            ticks=8,
            seed=5,
            controller=name,
        )
        out = tmp_path / name
        run_simulation(config, out)
        paths[name] = out
    gif_path = comparison_gif(paths, tmp_path / "cmp.gif", max_frames=10, cell=6)
    assert gif_path.exists()
    from PIL import Image

    frame = Image.open(gif_path)
    single = render_image(
        read_snapshot(paths["random"] / "snapshots" / "tick_000000.json"),
        cell=6,
    )
    assert frame.size[0] > single.size[0] * 2

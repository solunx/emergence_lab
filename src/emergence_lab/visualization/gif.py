from __future__ import annotations

from pathlib import Path

from PIL import Image

from emergence_lab.simulation.events import read_events
from emergence_lab.simulation.replay import iter_tick_states
from emergence_lab.simulation.snapshots import read_snapshot
from emergence_lab.visualization.renderer import render_panel
from emergence_lab.world.world import WorldState

WHITE = (255, 255, 255)
GUTTER = 4


def _stride(n_frames: int, max_frames: int) -> int:
    if n_frames <= max_frames:
        return 1
    return max(1, n_frames // max_frames)


def gif_from_run(
    run_dir: str | Path,
    out_path: str | Path | None = None,
    *,
    max_frames: int = 200,
    cell: int = 8,
    duration_ms: int = 80,
    label: str | None = None,
) -> Path:
    run_dir = Path(run_dir)
    initial = read_snapshot(run_dir / "snapshots" / "tick_000000.json")
    events = read_events(run_dir / "events.jsonl")
    frames = list(iter_tick_states(initial, events))
    stride = _stride(len(frames), max_frames)
    images = [
        render_panel(state, tick=tick, label=label, cell=cell)
        for i, (tick, state) in enumerate(frames)
        if i % stride == 0
    ]
    if not images:
        images = [render_panel(initial, tick=0, label=label, cell=cell)]
    out_path = Path(out_path) if out_path else run_dir / "run.gif"
    images[0].save(
        out_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
    )
    return out_path


def _compose_comparison(
    tick: int,
    panels: list[tuple[str, WorldState]],
    cell: int,
) -> Image.Image:
    rendered = [
        render_panel(state, tick=tick, label=name, cell=cell) for name, state in panels
    ]
    width = sum(img.width for img in rendered) + GUTTER * (len(rendered) + 1)
    height = max(img.height for img in rendered) + GUTTER * 2
    canvas = Image.new("RGB", (width, height), WHITE)
    x = GUTTER
    for img in rendered:
        canvas.paste(img, (x, GUTTER))
        x += img.width + GUTTER
    return canvas


def comparison_gif(
    run_dirs: dict[str, Path],
    out_path: str | Path,
    *,
    max_frames: int = 200,
    cell: int = 6,
    duration_ms: int = 80,
) -> Path:
    names = list(run_dirs)
    loaded: dict[str, list[tuple[int, WorldState]]] = {}
    for name, path in run_dirs.items():
        initial = read_snapshot(path / "snapshots" / "tick_000000.json")
        events = read_events(path / "events.jsonl")
        loaded[name] = list(iter_tick_states(initial, events))
    n = min(len(frames) for frames in loaded.values())
    stride = _stride(n, max_frames)
    images: list[Image.Image] = []
    for i in range(0, n, stride):
        tick = loaded[names[0]][i][0]
        panels = [(name, loaded[name][i][1]) for name in names]
        images.append(_compose_comparison(tick, panels, cell))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        out_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
    )
    return out_path

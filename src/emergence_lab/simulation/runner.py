"""Run a simulation, persist events/snapshots/metadata. Never overwrite results."""

from __future__ import annotations

import json
import subprocess
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from emergence_lab.config import SimConfig
from emergence_lab.simulation.engine import Engine, make_controller
from emergence_lab.simulation.rng import RNGBundle
from emergence_lab.simulation.snapshots import write_snapshot
from emergence_lab.world.world import WorldState, clone_world_for_controller, generate_world


def git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=Path(__file__).resolve().parents[3],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def unique_run_dir(root: Path, seed: int, controller: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"{controller}_seed{seed}_{stamp}"
    path = root / name
    path.mkdir(parents=True, exist_ok=False)
    return path


def layout_config(config: SimConfig) -> SimConfig:
    return replace(
        config,
        controller="random",
        genome_enabled=False,
        reproduction_enabled=False,
    )


def generate_layout(config: SimConfig) -> WorldState:
    rng = RNGBundle.from_seed(config.seed)
    return generate_world(layout_config(config), rng.world, rng.evolution)


def world_for_controller(layout: WorldState, config: SimConfig) -> WorldState:
    rng = RNGBundle.from_seed(config.seed)
    return clone_world_for_controller(layout, config, rng.evolution)


def run_simulation(
    config: SimConfig,
    out_dir: Path,
    *,
    layout: WorldState | None = None,
    check_invariants: bool = False,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = RNGBundle.from_seed(config.seed)
    if layout is None:
        state = generate_world(config, rng.world, rng.evolution)
    else:
        state = clone_world_for_controller(layout, config, rng.evolution)

    snapshots_dir = out_dir / "snapshots"
    write_snapshot(snapshots_dir / "tick_000000.json", state)

    controller = make_controller(config.controller, rng)
    engine = Engine(state, rng, controller, check_invariants=check_invariants)
    log = engine.run(config.ticks)
    log.write_jsonl(out_dir / "events.jsonl")

    every = max(1, config.snapshot_every)
    # End-of-run snapshot. Intermediate snapshots are written from the live state
    # only at the end here; tick 0 is the pre-run clone. Replay rebuilds the rest.
    write_snapshot(snapshots_dir / f"tick_{config.ticks:06d}.json", engine.state)

    metadata = {
        "experiment_id": config.experiment_id,
        "run_id": out_dir.name,
        "seed": config.seed,
        "controller_type": config.controller,
        "controller_version": "m1-v1",
        "world_version": "m1-v1",
        "config_version": "0.2",
        "git_commit": git_commit(),
        "ticks": config.ticks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_log_sha256": log.sha256(),
        "config": config.to_dict(),
        "determinism_notes": "Non-LLM controllers are bit-identical given code+config+seed.",
        "founders": engine.founders,
        "births": engine.births,
        "deaths": engine.deaths,
        "final_population": len(engine.state.living()),
    }
    with (out_dir / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)

    # Keep `every` referenced so configs remain meaningful for later snapshot policy.
    _ = every
    return out_dir


def run_same_world(
    config: SimConfig,
    controllers: list[str],
    out_root: Path,
    *,
    check_invariants: bool = False,
) -> dict[str, Path]:
    layout = generate_layout(config)
    shared = out_root / f"seed_{config.seed}_layout"
    shared.mkdir(parents=True, exist_ok=True)
    write_snapshot(shared / "tick_000000.json", layout)
    paths: dict[str, Path] = {}
    for name in controllers:
        run_config = replace(
            config,
            controller=name,
            reproduction_enabled=None,
            genome_enabled=None,
        )
        run_config.__post_init__()
        run_dir = unique_run_dir(out_root, config.seed, name)
        run_simulation(
            run_config,
            run_dir,
            layout=layout,
            check_invariants=check_invariants,
        )
        paths[name] = run_dir
    return paths

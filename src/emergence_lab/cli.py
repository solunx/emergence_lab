from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from emergence_lab.analytics.metrics import metrics_from_run, write_metrics_csv
from emergence_lab.analytics.statistics import paired_deltas
from emergence_lab.analytics.summarize import summarize_batch
from emergence_lab.config import SimConfig
from emergence_lab.simulation.runner import run_same_world, run_simulation, unique_run_dir
from emergence_lab.visualization.gif import comparison_gif, gif_from_run

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT / "experiments" / "results"


def _config_from_args(args: argparse.Namespace) -> SimConfig:
    config = SimConfig(
        seed=args.seed,
        ticks=args.ticks,
        controller=args.controller,
        experiment_id=args.experiment_id,
    )
    if args.config:
        config = SimConfig.from_yaml(args.config)
        if args.seed is not None:
            config.seed = args.seed
        if args.ticks is not None:
            config.ticks = args.ticks
        if args.controller is not None:
            config.controller = args.controller
            config.reproduction_enabled = None
            config.genome_enabled = None
            config.__post_init__()
    return config


def cmd_run(args: argparse.Namespace) -> None:
    config = _config_from_args(args)
    out = Path(args.out) if args.out else unique_run_dir(DEFAULT_RESULTS, config.seed, config.controller)
    run_simulation(config, out, check_invariants=args.invariants)
    metrics = metrics_from_run(out)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    if args.gif:
        gif_from_run(out, out / "run.gif", label=config.controller)
    print(out)


def cmd_compare(args: argparse.Namespace) -> None:
    config = _config_from_args(args)
    controllers = [item.strip() for item in args.controllers.split(",")]
    out_root = Path(args.out) if args.out else DEFAULT_RESULTS / (
        f"compare_seed{config.seed}_ticks{config.ticks}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    paths = run_same_world(config, controllers, out_root, check_invariants=args.invariants)
    rows = []
    for name, path in paths.items():
        metrics = metrics_from_run(path)
        metrics["controller"] = name
        metrics["seed"] = config.seed
        (path / "metrics.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8"
        )
        if args.gif:
            gif_from_run(path, path / "run.gif", label=name)
        rows.append(metrics)
        print(f"{name}: pop={metrics['final_population']} births={metrics['births']} dir={path}")
    write_metrics_csv(rows, out_root / "metrics.csv")
    if args.gif and len(paths) > 1:
        comparison_gif(paths, out_root / f"comparison_seed{config.seed}.gif")
    if len(rows) >= 2:
        for left, right in zip(controllers, controllers[1:]):
            delta = paired_deltas(rows, "final_population", left, right)
            print(delta.summary())


def cmd_gif(args: argparse.Namespace) -> None:
    path = gif_from_run(args.run_dir, args.out)
    print(path)


def cmd_summarize(args: argparse.Namespace) -> None:
    paths = summarize_batch(args.batch_dir, args.out, birth_threshold=args.birth_outlier)
    print((paths["aggregate"]).read_text(encoding="utf-8"), end="")
    print(f"Wrote {paths['aggregate']}")
    print(f"Wrote {paths['all_metrics']}")
    print(f"Wrote {paths['by_controller']}")
    print(f"Wrote {paths['paired_deltas']}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="emergence-lab")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run a single controller")
    run.add_argument("--config", type=str, default=None)
    run.add_argument("--seed", type=int, default=123456)
    run.add_argument("--ticks", type=int, default=200)
    run.add_argument("--controller", type=str, default="random")
    run.add_argument("--experiment-id", type=str, default="milestone1")
    run.add_argument("--out", type=str, default=None)
    run.add_argument("--gif", action="store_true")
    run.add_argument("--invariants", action="store_true")
    run.set_defaults(func=cmd_run)

    compare = sub.add_parser("compare", help="Same-world clones of C0/C1/C2")
    compare.add_argument("--config", type=str, default=None)
    compare.add_argument("--seed", type=int, default=123456)
    compare.add_argument("--ticks", type=int, default=200)
    compare.add_argument("--controller", type=str, default="random")
    compare.add_argument("--controllers", type=str, default="random,reactive,evolutionary")
    compare.add_argument("--experiment-id", type=str, default="milestone1")
    compare.add_argument("--out", type=str, default=None)
    compare.add_argument("--gif", action="store_true")
    compare.add_argument("--invariants", action="store_true")
    compare.set_defaults(func=cmd_compare)

    gif = sub.add_parser("gif", help="Render a GIF from a stored run (no resimulate)")
    gif.add_argument("run_dir")
    gif.add_argument("--out", type=str, default=None)
    gif.set_defaults(func=cmd_gif)

    summarize = sub.add_parser(
        "summarize",
        help="Aggregate batch metrics.csv files (no resimulate, no events.jsonl)",
    )
    summarize.add_argument("batch_dir", help="Folder containing seed_*/metrics.csv or a compare metrics.csv")
    summarize.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output directory (default: batch_dir)",
    )
    summarize.add_argument(
        "--birth-outlier",
        type=int,
        default=5,
        help="List seeds with at least this many births",
    )
    summarize.set_defaults(func=cmd_summarize)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from emergence_lab.analytics.metrics import metrics_from_run, write_metrics_csv
from emergence_lab.analytics.statistics import paired_deltas
from emergence_lab.analytics.summarize import batch_dir_for_compare_out, summarize_batch
from emergence_lab.batch import parse_controllers, parse_seed_spec, seed_is_complete
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


def run_compare_seed(
    config: SimConfig,
    controllers: list[str],
    out_root: Path,
    *,
    gif: bool = False,
    invariants: bool = False,
    summarize: bool = True,
    publish: bool = False,
) -> None:
    paths = run_same_world(config, controllers, out_root, check_invariants=invariants)
    rows = []
    for name, path in paths.items():
        metrics = metrics_from_run(path)
        metrics["controller"] = name
        metrics["seed"] = config.seed
        (path / "metrics.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8"
        )
        if gif:
            gif_from_run(path, path / "run.gif", label=name)
        rows.append(metrics)
        print(f"{name}: pop={metrics['final_population']} births={metrics['births']} dir={path}")
    write_metrics_csv(rows, out_root / "metrics.csv")
    if gif and len(paths) > 1:
        comparison_gif(paths, out_root / f"comparison_seed{config.seed}.gif")
    if len(rows) >= 2:
        for left, right in zip(controllers, controllers[1:]):
            delta = paired_deltas(rows, "final_population", left, right)
            print(delta.summary())
    if summarize:
        _summarize_and_maybe_publish(
            batch_dir_for_compare_out(out_root),
            publish=publish,
            quiet=True,
        )


def cmd_compare(args: argparse.Namespace) -> None:
    config = _config_from_args(args)
    controllers = parse_controllers(args.controllers)
    out_root = Path(args.out) if args.out else DEFAULT_RESULTS / (
        f"compare_seed{config.seed}_ticks{config.ticks}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    named_batch = args.out is not None
    run_compare_seed(
        config,
        controllers,
        out_root,
        gif=args.gif,
        invariants=args.invariants,
        summarize=not args.no_summarize,
        publish=named_batch and not args.no_publish,
    )


def cmd_batch(args: argparse.Namespace) -> None:
    seeds = parse_seed_spec(args.seeds)
    controllers = parse_controllers(args.controllers)
    experiment_id = args.experiment_id
    out_root = Path(args.out_root) if args.out_root else DEFAULT_RESULTS / experiment_id
    out_root.mkdir(parents=True, exist_ok=True)
    ran = 0
    skipped = 0
    for index, seed in enumerate(seeds, start=1):
        seed_dir = out_root / f"seed_{seed}"
        if seed_is_complete(seed_dir) and not args.force:
            print(f"[{index}/{len(seeds)}] skip seed {seed} (metrics.csv exists)")
            skipped += 1
            continue
        print(f"[{index}/{len(seeds)}] seed {seed}")
        config = SimConfig(
            seed=seed,
            ticks=args.ticks,
            experiment_id=experiment_id,
        )
        if args.config:
            config = SimConfig.from_yaml(args.config)
            config.seed = seed
            config.ticks = args.ticks
            config.experiment_id = experiment_id
            config.reproduction_enabled = None
            config.genome_enabled = None
            config.__post_init__()
        run_compare_seed(
            config,
            controllers,
            seed_dir,
            gif=args.gif,
            invariants=args.invariants,
            summarize=not args.no_summarize,
            publish=not args.no_publish,
        )
        ran += 1
    if not args.no_summarize and any(seed_is_complete(out_root / f"seed_{seed}") for seed in seeds):
        _summarize_and_maybe_publish(
            out_root,
            publish=not args.no_publish,
            quiet=True,
        )
    print(f"batch {experiment_id}: ran={ran} skipped={skipped} seeds={len(seeds)} out={out_root}")


def cmd_gif(args: argparse.Namespace) -> None:
    path = gif_from_run(args.run_dir, args.out)
    print(path)


def _summarize_and_maybe_publish(
    batch_dir: str | Path,
    *,
    out: str | Path | None = None,
    birth_threshold: int = 5,
    publish: bool = True,
    reports_dir: str | Path | None = None,
    lab_log: str | Path | None = None,
    quiet: bool = False,
) -> dict[str, Path]:
    paths = summarize_batch(
        batch_dir,
        out,
        birth_threshold=birth_threshold,
        publish=publish,
        reports_dir=reports_dir,
        lab_log=lab_log,
    )
    if not quiet:
        print((paths["aggregate"]).read_text(encoding="utf-8"), end="")
    print(f"Wrote {paths['aggregate']}")
    print(f"Wrote {paths['all_metrics']}")
    print(f"Wrote {paths['by_controller']}")
    print(f"Wrote {paths['paired_deltas']}")
    if "report" in paths:
        print(f"Published {paths['report']}")
    return paths


def cmd_summarize(args: argparse.Namespace) -> None:
    _summarize_and_maybe_publish(
        args.batch_dir,
        out=args.out,
        birth_threshold=args.birth_outlier,
        publish=not args.no_publish,
        reports_dir=args.reports_dir,
        lab_log=args.lab_log,
    )


def _add_compare_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--ticks", type=int, default=200)
    parser.add_argument("--controllers", type=str, default="random,reactive,evolutionary")
    parser.add_argument("--gif", action="store_true")
    parser.add_argument("--invariants", action="store_true")
    parser.add_argument(
        "--no-summarize",
        action="store_true",
        help="Skip rewriting aggregate.md",
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Write stats in results/ only; do not copy to experiments/reports/",
    )


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
    _add_compare_flags(compare)
    compare.add_argument("--seed", type=int, default=123456)
    compare.add_argument("--controller", type=str, default="random")
    compare.add_argument("--experiment-id", type=str, default="milestone1")
    compare.add_argument("--out", type=str, default=None)
    compare.set_defaults(func=cmd_compare)

    batch = sub.add_parser(
        "batch",
        help="Run a seed range into experiments/results/<experiment-id>/seed_N/",
    )
    _add_compare_flags(batch)
    batch.add_argument(
        "--experiment-id",
        type=str,
        required=True,
        help="Batch name; also the results folder name",
    )
    batch.add_argument(
        "--seeds",
        type=str,
        required=True,
        help="Seed list, e.g. 1-100 or 1,3,5-8",
    )
    batch.add_argument(
        "--out-root",
        type=str,
        default=None,
        help="Override experiments/results/<experiment-id>/",
    )
    batch.add_argument(
        "--force",
        action="store_true",
        help="Re-run seeds that already have metrics.csv",
    )
    batch.set_defaults(func=cmd_batch)

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
    summarize.add_argument(
        "--no-publish",
        action="store_true",
        help="Write stats in the batch folder only; do not copy to experiments/reports/",
    )
    summarize.add_argument(
        "--reports-dir",
        type=str,
        default=None,
        help="Override experiments/reports/ (tests and one-off copies)",
    )
    summarize.add_argument(
        "--lab-log",
        type=str,
        default=None,
        help="Override docs/lab_log.md",
    )
    summarize.set_defaults(func=cmd_summarize)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

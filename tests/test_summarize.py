import csv
import json
from pathlib import Path

from emergence_lab.analytics.statistics import paired_deltas
from emergence_lab.analytics.summarize import load_metric_rows, summarize_batch
from emergence_lab.cli import main


def _write_metrics(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "seed",
        "controller",
        "ticks",
        "final_population",
        "births",
        "deaths",
        "resources_consumed_count",
        "total_energy_final",
        "mean_population",
        "mean_energy",
        "action_entropy",
        "time_to_extinction",
        "invalid_action_rate",
        "run_dir",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_metadata(run_dir: Path, *, controller: str, seed: int, resource_value: int = 30) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "width": 32,
        "height": 32,
        "torus": True,
        "resource_count": 20,
        "resource_value": resource_value,
        "regen_delay": 15,
        "initial_population": 10,
        "ticks": 1000,
        "initial_energy": 100,
        "base_metabolism": 1,
        "movement_cost": 1,
        "reproduction_energy_threshold": 150,
        "reproduction_cost": 75,
        "observation_radius": 2,
        "mutation_probability": 0.05,
        "mutation_strength": 0.1,
        "genome_init_low": -0.1,
        "genome_init_high": 0.1,
        "memory_capacity": 20,
        "memory_entry_max_chars": 200,
        "snapshot_every": 100,
        "experiment_id": "test-batch",
        "seed": seed,
        "controller": controller,
        "reproduction_enabled": controller == "evolutionary",
        "genome_enabled": controller == "evolutionary",
        "extra": {},
    }
    payload = {
        "config": config,
        "config_version": "0.2",
        "world_version": "m1-v1",
        "controller_version": "m1-v1",
        "git_commit": None,
        "controller_type": controller,
        "seed": seed,
    }
    (run_dir / "metadata.json").write_text(json.dumps(payload), encoding="utf-8")


def _batch(tmp_path: Path) -> Path:
    root = tmp_path / "batch"
    _write_metrics(
        root / "seed_1" / "metrics.csv",
        [
            {
                "seed": 1,
                "controller": "random",
                "ticks": 1000,
                "final_population": 0,
                "births": 0,
                "deaths": 10,
                "resources_consumed_count": 6,
                "total_energy_final": 0,
                "mean_population": 0.6,
                "mean_energy": 40,
                "action_entropy": 2.3,
                "time_to_extinction": 100,
                "invalid_action_rate": 0,
                "run_dir": "r1",
            },
            {
                "seed": 1,
                "controller": "reactive",
                "ticks": 1000,
                "final_population": 2,
                "births": 0,
                "deaths": 8,
                "resources_consumed_count": 200,
                "total_energy_final": 800,
                "mean_population": 3.0,
                "mean_energy": 200,
                "action_entropy": 2.3,
                "time_to_extinction": "",
                "invalid_action_rate": 0,
                "run_dir": "c1",
            },
            {
                "seed": 1,
                "controller": "evolutionary",
                "ticks": 1000,
                "final_population": 0,
                "births": 0,
                "deaths": 10,
                "resources_consumed_count": 8,
                "total_energy_final": 0,
                "mean_population": 0.7,
                "mean_energy": 30,
                "action_entropy": 1.8,
                "time_to_extinction": 120,
                "invalid_action_rate": 0,
                "run_dir": "e1",
            },
        ],
    )
    _write_metrics(
        root / "seed_2" / "metrics.csv",
        [
            {
                "seed": 2,
                "controller": "random",
                "ticks": 1000,
                "final_population": 0,
                "births": 0,
                "deaths": 10,
                "resources_consumed_count": 7,
                "total_energy_final": 0,
                "mean_population": 0.5,
                "mean_energy": 40,
                "action_entropy": 2.3,
                "time_to_extinction": 90,
                "invalid_action_rate": 0,
                "run_dir": "r2",
            },
            {
                "seed": 2,
                "controller": "reactive",
                "ticks": 1000,
                "final_population": 3,
                "births": 0,
                "deaths": 7,
                "resources_consumed_count": 250,
                "total_energy_final": 900,
                "mean_population": 4.0,
                "mean_energy": 220,
                "action_entropy": 2.3,
                "time_to_extinction": "",
                "invalid_action_rate": 0,
                "run_dir": "c2",
            },
            {
                "seed": 2,
                "controller": "evolutionary",
                "ticks": 1000,
                "final_population": 2,
                "births": 9,
                "deaths": 17,
                "resources_consumed_count": 100,
                "total_energy_final": 150,
                "mean_population": 2.0,
                "mean_energy": 80,
                "action_entropy": 1.5,
                "time_to_extinction": "",
                "invalid_action_rate": 0,
                "run_dir": "e2",
            },
        ],
    )
    _write_metrics(
        root / "seed_3" / "metrics.csv",
        [
            {
                "seed": 3,
                "controller": "random",
                "ticks": 1000,
                "final_population": 0,
                "births": 0,
                "deaths": 10,
                "resources_consumed_count": 5,
                "total_energy_final": 0,
                "mean_population": 0.4,
                "mean_energy": 35,
                "action_entropy": 2.3,
                "time_to_extinction": 80,
                "invalid_action_rate": 0,
                "run_dir": "r3",
            },
            {
                "seed": 3,
                "controller": "reactive",
                "ticks": 1000,
                "final_population": 0,
                "births": 0,
                "deaths": 10,
                "resources_consumed_count": 20,
                "total_energy_final": 0,
                "mean_population": 1.0,
                "mean_energy": 50,
                "action_entropy": 2.3,
                "time_to_extinction": 400,
                "invalid_action_rate": 0,
                "run_dir": "c3",
            },
            {
                "seed": 3,
                "controller": "evolutionary",
                "ticks": 1000,
                "final_population": 0,
                "births": 1,
                "deaths": 11,
                "resources_consumed_count": 12,
                "total_energy_final": 0,
                "mean_population": 0.8,
                "mean_energy": 40,
                "action_entropy": 1.9,
                "time_to_extinction": 200,
                "invalid_action_rate": 0,
                "run_dir": "e3",
            },
        ],
    )
    (root / "seed_2" / "evolutionary_seed2" / "events.jsonl").parent.mkdir(parents=True, exist_ok=True)
    (root / "seed_2" / "evolutionary_seed2" / "events.jsonl").write_text(
        "this file must not be read\n", encoding="utf-8"
    )
    for seed, controller, name in (
        (1, "random", "r1"),
        (1, "reactive", "c1"),
        (1, "evolutionary", "e1"),
        (2, "random", "r2"),
        (2, "reactive", "c2"),
        (2, "evolutionary", "e2"),
        (3, "random", "r3"),
        (3, "reactive", "c3"),
        (3, "evolutionary", "e3"),
    ):
        _write_metadata(root / name, controller=controller, seed=seed)
    return root


def test_summarize_reads_metrics_csv_only(tmp_path):
    root = _batch(tmp_path)
    rows = load_metric_rows(root)
    assert len(rows) == 9
    assert {row["seed"] for row in rows} == {1, 2, 3}
    reactive = [row for row in rows if row["controller"] == "reactive"]
    assert sum(row["survived"] for row in reactive) == 2
    evo = [row for row in rows if row["controller"] == "evolutionary"]
    assert sum(row["any_birth"] for row in evo) == 2
    censored = next(row for row in reactive if row["seed"] == 1)
    assert censored["time_to_extinction"] is None
    assert censored["time_to_extinction_censored"] == 1000


def test_paired_population_delta(tmp_path):
    rows = load_metric_rows(_batch(tmp_path))
    delta = paired_deltas(rows, "final_population", "reactive", "random")
    assert delta.deltas == [2.0, 3.0, 0.0]
    summary = delta.summary()
    assert summary["n"] == 3
    assert summary["mean_delta"] == 5 / 3
    assert summary["n_pos"] == 2
    assert summary["n_zero"] == 1
    assert summary["n_neg"] == 0


def test_summarize_writes_small_artifacts(tmp_path):
    root = _batch(tmp_path)
    out = tmp_path / "summary_out"
    paths = summarize_batch(root, out, birth_threshold=5)
    markdown = paths["aggregate"].read_text(encoding="utf-8")
    assert "seeds: **3**" in markdown
    assert "reactive" in markdown
    assert "seed 2 evolutionary" in markdown
    assert "`resource_value` | 30" in markdown or "| `resource_value` | 30 |" in markdown
    assert "| MOVE cost | 2" in markdown
    assert "5×5 egocentric" in markdown
    assert "| evolutionary | yes | yes |" in markdown
    assert "events.jsonl" in markdown  # the disclaimer, not a read
    all_rows = list(csv.DictReader(paths["all_metrics"].open()))
    assert len(all_rows) == 9
    paired = list(csv.DictReader(paths["paired_deltas"].open()))
    assert any(row["metric"] == "final_population" and row["a"] == "reactive" for row in paired)
    # Second pass must not ingest its own output files if written into the batch.
    summarize_batch(root, root, birth_threshold=5)
    again = load_metric_rows(root)
    assert len(again) == 9


def test_cli_summarize(tmp_path, capsys):
    root = _batch(tmp_path)
    main(["summarize", str(root)])
    captured = capsys.readouterr().out
    assert "Alive" in captured
    assert "## Parameters" in captured
    assert (root / "aggregate.md").exists()


def test_parameter_mismatch_is_flagged(tmp_path):
    root = _batch(tmp_path)
    _write_metadata(root / "e2", controller="evolutionary", seed=2, resource_value=20)
    markdown = summarize_batch(root, tmp_path / "out").get("aggregate").read_text(encoding="utf-8")
    assert "shared parameters differ" in markdown
    assert "`resource_value`" in markdown
    assert "20" in markdown

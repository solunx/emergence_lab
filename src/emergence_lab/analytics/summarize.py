"""Offline batch summaries from metrics.csv. Never reads events.jsonl."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from emergence_lab.analytics.report import publish_report
from emergence_lab.analytics.statistics import ci95, cohens_d, mean, median, paired_deltas, sd
from emergence_lab.world.types import N_FEATURES, N_GENOME_WEIGHTS

OUTPUT_NAMES = frozenset(
    {
        "all_metrics.csv",
        "by_controller.csv",
        "paired_deltas.csv",
        "aggregate.md",
    }
)

CONTROLLER_ORDER = (
    "random",
    "random_r",
    "reactive",
    "reactive_r",
    "evolutionary",
    "evolutionary_oracle",
    "evolutionary_oracle_r",
    "llm",
    "llm_a",
    "llm_b",
    "llm_memory",
    "llm_evolution",
    "llm_evolution_memory",
)

NUMERIC_FIELDS = (
    "ticks",
    "final_population",
    "mean_population",
    "births",
    "deaths",
    "birth_rate",
    "death_rate",
    "time_to_extinction",
    "time_to_first_birth",
    "max_generation",
    "founders_reproducing_count",
    "mean_energy",
    "energy_variance",
    "total_energy_final",
    "resources_consumed_count",
    "action_entropy",
    "invalid_action_rate",
    "llm_calls",
    "llm_mean_latency_ms",
)

PRIMARY_METRICS = (
    "survived",
    "any_birth",
    "final_population",
    "births",
    "deaths",
    "resources_consumed_count",
    "total_energy_final",
    "mean_population",
    "mean_energy",
    "action_entropy",
    "invalid_action_rate",
    "time_to_extinction",
    "time_to_extinction_censored",
    "time_to_first_birth",
    "max_generation",
    "founders_reproducing_count",
)

PER_RUN_CONFIG_KEYS = frozenset(
    {"seed", "controller", "extra", "reproduction_enabled", "genome_enabled"}
)

PARAM_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("World", ("width", "height", "torus")),
    ("Resources", ("resource_count", "resource_value", "regen_delay")),
    ("Population", ("initial_population",)),
    (
        "Organism / energy",
        ("initial_energy", "base_metabolism", "movement_cost"),
    ),
    (
        "Reproduction / genome",
        (
            "reproduction_energy_threshold",
            "reproduction_cost",
            "mutation_probability",
            "mutation_strength",
            "genome_init_low",
            "genome_init_high",
        ),
    ),
    (
        "Observation / memory",
        ("observation_radius", "memory_capacity", "memory_entry_max_chars"),
    ),
    ("Simulation", ("ticks", "snapshot_every", "experiment_id")),
    (
        "LLM",
        (
            "llm_model",
            "llm_endpoint",
            "llm_temperature",
            "llm_prompt_id",
            "llm_prompt_version",
            "llm_num_predict",
        ),
    ),
)

META_VERSION_KEYS = (
    "config_version",
    "world_version",
    "controller_version",
    "git_commit",
)


def _is_missing(value: object) -> bool:
    return value is None or value == ""


def _as_float(value: object) -> float | None:
    if _is_missing(value):
        return None
    return float(value)


def _fmt(value: float | None, digits: int = 2) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    if digits == 0:
        return str(int(round(value)))
    return f"{value:.{digits}f}"


def _fmt_pct(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return f"{value:.1f}%"


def discover_metrics_csvs(batch_dir: Path) -> list[Path]:
    """Find per-run metrics.csv files without walking snapshot/event trees."""
    seed_hits = sorted(
        path
        for path in batch_dir.glob("seed_*/metrics.csv")
        if path.name not in OUTPUT_NAMES
    )
    if seed_hits:
        return seed_hits
    direct = batch_dir / "metrics.csv"
    if direct.is_file():
        return [direct]
    child_hits = sorted(
        path
        for path in batch_dir.glob("*/metrics.csv")
        if path.name not in OUTPUT_NAMES
    )
    if child_hits:
        return child_hits
    return [
        path
        for path in sorted(batch_dir.rglob("metrics.csv"))
        if path.name not in OUTPUT_NAMES
    ]


def _parse_seed(raw: object, csv_path: Path) -> int:
    parsed = _as_float(raw)
    if parsed is not None:
        return int(parsed)
    parent = csv_path.parent.name
    if parent.startswith("seed_"):
        return int(parent.split("_", 1)[1])
    raise ValueError(f"Cannot infer seed from {csv_path}")


def load_metric_rows(batch_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(batch_dir)
    csv_paths = discover_metrics_csvs(root)
    if not csv_paths:
        raise FileNotFoundError(f"No metrics.csv files under {root}")
    rows: list[dict[str, Any]] = []
    for path in csv_paths:
        with path.open(encoding="utf-8", newline="") as handle:
            for raw in csv.DictReader(handle):
                row: dict[str, Any] = dict(raw)
                row["seed"] = _parse_seed(row.get("seed"), path)
                row["controller"] = str(row.get("controller") or "").strip()
                if not row["controller"]:
                    raise ValueError(f"Missing controller in {path}")
                for field in NUMERIC_FIELDS:
                    row[field] = _as_float(row.get(field))
                ticks = row.get("ticks") or 0.0
                pop = row.get("final_population") or 0.0
                births = row.get("births") or 0.0
                row["survived"] = 1.0 if pop > 0 else 0.0
                row["any_birth"] = 1.0 if births > 0 else 0.0
                tte = row.get("time_to_extinction")
                row["time_to_extinction_censored"] = tte if tte is not None else ticks
                row["source_csv"] = str(path)
                rows.append(row)
    rows.sort(key=lambda item: (item["seed"], item["controller"]))
    return rows


def _resolve_run_dir(raw: object, source_csv: Path, batch_dir: Path) -> Path | None:
    if _is_missing(raw):
        return None
    path = Path(str(raw))
    candidates = [
        path,
        batch_dir / path,
        source_csv.parent / path,
        source_csv.parent / path.name,
        Path.cwd() / path,
    ]
    for candidate in candidates:
        if (candidate / "metadata.json").is_file():
            return candidate
    return None


def _load_metadata(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _json_key(value: object) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def collect_batch_parameters(
    rows: list[dict[str, Any]],
    batch_dir: Path,
) -> dict[str, Any]:
    """Read metadata.json next to each run. Never opens events.jsonl."""
    records: list[dict[str, Any]] = []
    missing = 0
    for row in rows:
        run_dir = _resolve_run_dir(row.get("run_dir"), Path(row["source_csv"]), batch_dir)
        if run_dir is None:
            missing += 1
            continue
        meta = _load_metadata(run_dir / "metadata.json")
        if not meta:
            missing += 1
            continue
        config = meta.get("config") if isinstance(meta.get("config"), dict) else {}
        records.append(
            {
                "seed": row["seed"],
                "controller": row["controller"],
                "config": config,
                "meta": {key: meta.get(key) for key in META_VERSION_KEYS},
            }
        )

    shared_values: dict[str, Counter[str]] = defaultdict(Counter)
    shared_decoded: dict[str, dict[str, object]] = defaultdict(dict)
    controller_flags: dict[str, Counter[str]] = defaultdict(Counter)
    version_values: dict[str, Counter[str]] = defaultdict(Counter)
    version_decoded: dict[str, dict[str, object]] = defaultdict(dict)

    for record in records:
        config = record["config"]
        for key, value in config.items():
            if key in PER_RUN_CONFIG_KEYS:
                continue
            token = _json_key(value)
            shared_values[key][token] += 1
            shared_decoded[key][token] = value
        flags = {
            "reproduction_enabled": bool(config.get("reproduction_enabled")),
            "genome_enabled": bool(config.get("genome_enabled")),
        }
        controller_flags[record["controller"]][_json_key(flags)] += 1
        for key, value in record["meta"].items():
            token = _json_key(value)
            version_values[key][token] += 1
            version_decoded[key][token] = value

    def consensus(counters: dict[str, Counter[str]], decoded: dict[str, dict[str, object]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, counter in counters.items():
            token, _count = counter.most_common(1)[0]
            out[key] = decoded[key][token]
        return out

    mismatches = []
    for key, counter in sorted(shared_values.items()):
        if len(counter) > 1:
            mismatches.append(
                {
                    "key": key,
                    "values": [
                        {"value": shared_decoded[key][token], "n": count}
                        for token, count in counter.most_common()
                    ],
                }
            )
    for key, counter in sorted(version_values.items()):
        if len(counter) > 1:
            mismatches.append(
                {
                    "key": key,
                    "values": [
                        {"value": version_decoded[key][token], "n": count}
                        for token, count in counter.most_common()
                    ],
                }
            )

    flags_by_controller = {}
    for controller, counter in controller_flags.items():
        token, _count = counter.most_common(1)[0]
        flags_by_controller[controller] = json.loads(token)

    return {
        "n_metadata": len(records),
        "n_missing": missing,
        "shared": consensus(shared_values, shared_decoded),
        "versions": consensus(version_values, version_decoded),
        "controller_flags": flags_by_controller,
        "mismatches": mismatches,
    }


def _yes_no(value: object) -> str:
    return "yes" if value else "no"


def _display(value: object) -> str:
    if isinstance(value, bool):
        return _yes_no(value)
    if value is None:
        return "—"
    return str(value)


def render_parameters_md(params: dict[str, Any], controllers: list[str]) -> list[str]:
    lines = ["## Parameters", ""]
    found = params["n_metadata"]
    missing = params["n_missing"]
    if found == 0:
        lines.append("No `metadata.json` found next to `run_dir`. Stats below are still from `metrics.csv`.")
        lines.append("")
        return lines
    lines.append(
        f"From **{found}** `metadata.json` file(s)"
        + (f"; **{missing}** run(s) had none." if missing else ".")
        + " Shared world fields should be identical across clones; seed and controller differ by design."
    )
    lines.append("")
    shared: dict[str, Any] = params["shared"]
    grouped_keys: set[str] = set()
    for title, keys in PARAM_GROUPS:
        present = [key for key in keys if key in shared]
        if not present:
            continue
        grouped_keys.update(present)
        lines.append(f"### {title}")
        lines.append("")
        lines.append("| Parameter | Value |")
        lines.append("|---|---|")
        for key in present:
            lines.append(f"| `{key}` | {_display(shared[key])} |")
        if title == "Organism / energy":
            base = shared.get("base_metabolism")
            move = shared.get("movement_cost")
            if isinstance(base, (int, float)) and isinstance(move, (int, float)):
                lines.append(f"| STAY cost | {_display(base)} (`base_metabolism`) |")
                lines.append(f"| MOVE cost | {_display(base + move)} (`base_metabolism` + `movement_cost`) |")
        if title == "Resources":
            lines.append("| spawn under organism | no |")
        if title == "Reproduction / genome":
            lines.append("| child energy | same as `reproduction_cost` |")
            lines.append(f"| genome weights | {N_GENOME_WEIGHTS} ({N_FEATURES} features × 5 actions) |")
            lines.append("| C2 policy | linear argmax, no hidden exploration term |")
        if title == "Observation / memory":
            radius = shared.get("observation_radius")
            if isinstance(radius, (int, float)):
                side = int(radius) * 2 + 1
                lines.append(f"| observation window | {side}×{side} egocentric |")
            lines.append("| global coords / IDs / others' energy | no |")
        lines.append("")
    other = [key for key in sorted(shared) if key not in grouped_keys]
    if other:
        lines.append("### Other config")
        lines.append("")
        lines.append("| Parameter | Value |")
        lines.append("|---|---|")
        for key in other:
            lines.append(f"| `{key}` | {_display(shared[key])} |")
        lines.append("")

    flags = params.get("controller_flags") or {}
    if flags:
        lines.append("### Controller flags")
        lines.append("")
        lines.append("| Controller | Reproduction | Genome |")
        lines.append("|---|---|---|")
        for controller in controllers:
            item = flags.get(controller, {})
            lines.append(
                f"| {controller} | {_yes_no(item.get('reproduction_enabled'))} | "
                f"{_yes_no(item.get('genome_enabled'))} |"
            )
        lines.append("")
        lines.append(
            "Reproduction is not a universal world rule. C2 vs C0/C1 mixes decision policy with population dynamics."
        )
        lines.append("")

    versions = params.get("versions") or {}
    if any(value is not None for value in versions.values()):
        lines.append("### Versions")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        for key in META_VERSION_KEYS:
            if key in versions:
                lines.append(f"| `{key}` | {_display(versions[key])} |")
        lines.append("")

    mismatches = params.get("mismatches") or []
    if mismatches:
        lines.append("**Warning:** shared parameters differ across runs in this batch:")
        for item in mismatches:
            parts = ", ".join(f"`{_display(entry['value'])}` (n={entry['n']})" for entry in item["values"])
            lines.append(f"- `{item['key']}`: {parts}")
        lines.append("")
    return lines


def controller_order(rows: Iterable[dict[str, Any]]) -> list[str]:
    seen = {str(row["controller"]) for row in rows}
    ordered = [name for name in CONTROLLER_ORDER if name in seen]
    ordered.extend(sorted(seen - set(ordered)))
    return ordered


def comparison_pairs(controllers: list[str]) -> list[tuple[str, str]]:
    """Later matrix condition minus earlier (treatment − baseline)."""
    pairs = []
    for i, later in enumerate(controllers):
        for earlier in controllers[:i]:
            pairs.append((later, earlier))
    return pairs


def describe(values: list[float]) -> dict[str, float]:
    lo, hi = ci95(values)
    return {
        "n": float(len(values)),
        "mean": mean(values),
        "median": median(values),
        "sd": sd(values),
        "ci95_lo": lo,
        "ci95_hi": hi,
        "min": min(values) if values else float("nan"),
        "max": max(values) if values else float("nan"),
    }


def by_controller_rows(rows: list[dict[str, Any]], metrics: tuple[str, ...] = PRIMARY_METRICS) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["controller"]].append(row)
    out = []
    for controller in controller_order(rows):
        group = grouped[controller]
        n = len(group)
        for metric in metrics:
            values = [float(item[metric]) for item in group if item.get(metric) is not None]
            stats = describe(values)
            out.append(
                {
                    "controller": controller,
                    "metric": metric,
                    "n_runs": n,
                    "n_values": int(stats["n"]),
                    "mean": stats["mean"],
                    "median": stats["median"],
                    "sd": stats["sd"],
                    "ci95_lo": stats["ci95_lo"],
                    "ci95_hi": stats["ci95_hi"],
                    "min": stats["min"],
                    "max": stats["max"],
                }
            )
    return out


def paired_delta_rows(
    rows: list[dict[str, Any]],
    metrics: tuple[str, ...] = PRIMARY_METRICS,
) -> list[dict[str, Any]]:
    out = []
    for later, earlier in comparison_pairs(controller_order(rows)):
        for metric in metrics:
            delta = paired_deltas(rows, metric, later, earlier)
            if not delta.deltas:
                continue
            summary = delta.summary()
            a_vals = [
                float(row[metric])
                for row in rows
                if row["controller"] == later and row.get(metric) is not None
            ]
            b_vals = [
                float(row[metric])
                for row in rows
                if row["controller"] == earlier and row.get(metric) is not None
            ]
            summary["cohens_d_unpaired"] = cohens_d(a_vals, b_vals)
            out.append(summary)
    return out


def _int_distribution(rows: list[dict[str, Any]], metric: str) -> dict[int, int]:
    counts: Counter[int] = Counter()
    for row in rows:
        value = row.get(metric)
        if value is None:
            continue
        counts[int(value)] += 1
    return dict(sorted(counts.items()))


def _controller_groups(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["controller"]].append(row)
    return grouped


def outlier_seeds(
    rows: list[dict[str, Any]],
    birth_threshold: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    grouped = _controller_groups(rows)
    survivors = []
    high_births = []
    extinct_usually_alive = []
    for controller, group in grouped.items():
        alive_frac = mean([row["survived"] for row in group])
        for row in group:
            compact = {
                "seed": row["seed"],
                "controller": controller,
                "final_population": row["final_population"],
                "births": row["births"],
                "resources_consumed_count": row["resources_consumed_count"],
                "total_energy_final": row["total_energy_final"],
                "time_to_extinction": row["time_to_extinction"],
            }
            if row["survived"] > 0 and alive_frac < 0.5:
                survivors.append(compact)
            if (row.get("births") or 0) >= birth_threshold:
                high_births.append(compact)
            if row["survived"] == 0 and alive_frac >= 0.5:
                extinct_usually_alive.append(compact)
    survivors.sort(key=lambda item: (-(item["final_population"] or 0), item["seed"]))
    high_births.sort(key=lambda item: (-(item["births"] or 0), item["seed"]))
    extinct_usually_alive.sort(key=lambda item: (item["controller"], item["seed"]))
    return {
        "survivors_non_reactive": survivors,
        "high_births": high_births,
        "extinct_despite_usual_survival": extinct_usually_alive,
    }


def render_aggregate_md(
    rows: list[dict[str, Any]],
    batch_dir: Path,
    birth_threshold: int = 5,
) -> str:
    controllers = controller_order(rows)
    grouped = _controller_groups(rows)
    n_seeds = len({row["seed"] for row in rows})
    ticks = {int(row["ticks"]) for row in rows if row.get("ticks") is not None}
    ticks_label = ",".join(str(t) for t in sorted(ticks)) if ticks else "?"
    lines = [
        f"# Aggregate results — `{batch_dir.name}`",
        "",
        "Deterministic numbers from `metrics.csv` plus run `metadata.json` parameters. No resimulate, no `events.jsonl`, no LLM.",
        "",
        f"- seeds: **{n_seeds}**",
        f"- controller-runs: **{len(rows)}**",
        f"- ticks: **{ticks_label}**",
        f"- controllers: {', '.join(controllers)}",
        "",
    ]
    params = collect_batch_parameters(rows, batch_dir)
    lines.extend(render_parameters_md(params, controllers))
    lines.extend(
        [
            "## Survival and births",
            "",
            "| Controller | n | Alive | Alive% | Any birth | Any birth% | Mean pop | Med pop | Mean births | Med births | Mean food | Med food | Mean energy |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    by_metric = {(item["controller"], item["metric"]): item for item in by_controller_rows(rows)}
    for controller in controllers:
        n = len(grouped[controller])
        alive_n = sum(1 for row in grouped[controller] if row["survived"] > 0)
        birth_n = sum(1 for row in grouped[controller] if row["any_birth"] > 0)
        pop = by_metric[(controller, "final_population")]
        births = by_metric[(controller, "births")]
        food = by_metric[(controller, "resources_consumed_count")]
        energy = by_metric[(controller, "total_energy_final")]
        lines.append(
            "| "
            + " | ".join(
                [
                    controller,
                    str(n),
                    str(alive_n),
                    _fmt_pct(100 * alive_n / n if n else float("nan")),
                    str(birth_n),
                    _fmt_pct(100 * birth_n / n if n else float("nan")),
                    _fmt(pop["mean"]),
                    _fmt(pop["median"]),
                    _fmt(births["mean"]),
                    _fmt(births["median"]),
                    _fmt(food["mean"], 1),
                    _fmt(food["median"], 1),
                    _fmt(energy["mean"], 1),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Time to extinction", "", "| Controller | Extinct | Extinct% | Mean TTE (extinct) | Med TTE | Mean TTE (censored) | Med TTE (censored) |", "|---|---:|---:|---:|---:|---:|---:|"])
    for controller in controllers:
        extinct = by_metric[(controller, "time_to_extinction")]
        censored = by_metric[(controller, "time_to_extinction_censored")]
        n = len(grouped[controller])
        extinct_n = extinct["n_values"]
        lines.append(
            "| "
            + " | ".join(
                [
                    controller,
                    str(extinct_n),
                    _fmt_pct(100 * extinct_n / n if n else float("nan")),
                    _fmt(extinct["mean"], 1),
                    _fmt(extinct["median"], 1),
                    _fmt(censored["mean"], 1),
                    _fmt(censored["median"], 1),
                ]
            )
            + " |"
        )
    lines.extend(["", "Censored TTE treats survivors as lasting the full run.", ""])

    lines.extend(
        [
            "## Reproduction timing",
            "",
            "| Controller | Any birth% | Mean founders reproducing | Mean max generation | Mean time to first birth | Med first birth |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for controller in controllers:
        n = len(grouped[controller])
        birth_n = sum(1 for row in grouped[controller] if row["any_birth"] > 0)
        founders = by_metric[(controller, "founders_reproducing_count")]
        max_gen = by_metric[(controller, "max_generation")]
        first = by_metric[(controller, "time_to_first_birth")]
        lines.append(
            "| "
            + " | ".join(
                [
                    controller,
                    _fmt_pct(100 * birth_n / n if n else float("nan")),
                    _fmt(founders["mean"], 2),
                    _fmt(max_gen["mean"], 2),
                    _fmt(first["mean"], 1),
                    _fmt(first["median"], 1),
                ]
            )
            + " |"
        )
    lines.extend(["", "Time to first birth is among runs that had at least one birth. Max generation 0 means only founders.", ""])

    lines.extend(["## Distributions", ""])
    for controller in controllers:
        pop_dist = _int_distribution(grouped[controller], "final_population")
        birth_dist = _int_distribution(grouped[controller], "births")
        lines.append(f"- **{controller}** final pop `{pop_dist}`; births `{birth_dist}`")
    lines.append("")

    lines.extend(
        [
            "## Paired Δ (later − earlier, same seed)",
            "",
            "| Metric | A − B | n | Mean Δ | Med Δ | 95% CI | Cohen's d (paired) | + / = / − |",
            "|---|---|---:|---:|---:|---|---:|---:|",
        ]
    )
    pair_metrics = (
        "final_population",
        "births",
        "resources_consumed_count",
        "total_energy_final",
        "time_to_extinction_censored",
        "time_to_first_birth",
        "max_generation",
        "survived",
    )
    for item in paired_delta_rows(rows, pair_metrics):
        lines.append(
            "| "
            + " | ".join(
                [
                    item["metric"],
                    f"{item['a']} − {item['b']}",
                    str(item["n"]),
                    _fmt(item["mean_delta"]),
                    _fmt(item["median_delta"]),
                    f"[{_fmt(item['ci95_lo'])}, {_fmt(item['ci95_hi'])}]",
                    _fmt(item["cohens_d_paired"]),
                    f"{item['n_pos']} / {item['n_zero']} / {item['n_neg']}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Δ_i = metric(A, seed_i) − metric(B, seed_i). `+ / = / −` is seeds where A is higher / tied / lower.",
            "Reproduction is not a universal world rule: C2 vs C0/C1 mixes decision policy with population dynamics.",
            "",
        ]
    )

    outliers = outlier_seeds(rows, birth_threshold=birth_threshold)
    lines.append("## Outlier seeds (for follow-up GIFs, not evidence)")
    lines.append("")
    if outliers["survivors_non_reactive"]:
        lines.append(f"Non-reactive survivors (n={len(outliers['survivors_non_reactive'])}):")
        for item in outliers["survivors_non_reactive"]:
            lines.append(
                f"- seed {item['seed']} {item['controller']}: pop={_fmt(item['final_population'], 0)} "
                f"births={_fmt(item['births'], 0)} food={_fmt(item['resources_consumed_count'], 0)} "
                f"energy={_fmt(item['total_energy_final'], 0)}"
            )
        lines.append("")
    else:
        lines.append("No non-reactive survivors.")
        lines.append("")
    if outliers["high_births"]:
        lines.append(f"Births ≥ {birth_threshold}:")
        for item in outliers["high_births"]:
            tte = item["time_to_extinction"]
            tte_s = "alive" if tte is None else f"extinct@{_fmt(tte, 0)}"
            lines.append(
                f"- seed {item['seed']} {item['controller']}: births={_fmt(item['births'], 0)} "
                f"pop={_fmt(item['final_population'], 0)} {tte_s}"
            )
        lines.append("")
    if outliers["extinct_despite_usual_survival"]:
        lines.append("Extinct in a controller that usually survives:")
        for item in outliers["extinct_despite_usual_survival"]:
            lines.append(
                f"- seed {item['seed']} {item['controller']}: tte={_fmt(item['time_to_extinction'], 0)} "
                f"food={_fmt(item['resources_consumed_count'], 0)}"
            )
        lines.append("")
    lines.append("A visually interesting GIF is not evidence of emergence.")
    lines.append("")
    return "\n".join(lines)


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = fieldnames or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {}
            for key in keys:
                value = row.get(key)
                out[key] = "" if value is None else value
            writer.writerow(out)


def summarize_batch(
    batch_dir: str | Path,
    out_dir: str | Path | None = None,
    birth_threshold: int = 5,
    *,
    publish: bool = False,
    reports_dir: str | Path | None = None,
    lab_log: str | Path | None = None,
) -> dict[str, Path]:
    root = Path(batch_dir)
    dest = Path(out_dir) if out_dir else root
    dest.mkdir(parents=True, exist_ok=True)
    rows = load_metric_rows(root)
    all_path = dest / "all_metrics.csv"
    by_path = dest / "by_controller.csv"
    paired_path = dest / "paired_deltas.csv"
    md_path = dest / "aggregate.md"
    export_fields = [
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
        "time_to_extinction_censored",
        "time_to_first_birth",
        "max_generation",
        "founders_reproducing_count",
        "survived",
        "any_birth",
        "invalid_action_rate",
        "run_dir",
        "source_csv",
    ]
    _write_csv(all_path, rows, export_fields)
    _write_csv(by_path, by_controller_rows(rows))
    _write_csv(paired_path, paired_delta_rows(rows))
    markdown = render_aggregate_md(rows, root, birth_threshold=birth_threshold)
    md_path.write_text(markdown, encoding="utf-8")
    paths = {
        "all_metrics": all_path,
        "by_controller": by_path,
        "paired_deltas": paired_path,
        "aggregate": md_path,
    }
    if publish:
        paths["report"] = publish_report(
            dest,
            reports_dir=reports_dir,
            lab_log=lab_log,
            batch_id=root.name,
        )
    return paths


def batch_dir_for_compare_out(out_root: str | Path) -> Path:
    """If compare wrote seed_N/, summarize the parent batch folder."""
    path = Path(out_root)
    if path.name.startswith("seed_"):
        return path.parent
    return path

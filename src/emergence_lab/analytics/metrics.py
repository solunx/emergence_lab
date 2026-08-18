from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path
from typing import Any

from emergence_lab.simulation.events import read_events


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = _mean(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


def metrics_from_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    tick_rows = [
        e for e in events if e.get("event") == "TICK_FINISHED" and e.get("phase") != "initial"
    ]
    births = sum(1 for e in events if e["event"] == "BIRTH")
    deaths = sum(1 for e in events if e["event"] == "DEATH")
    consumed = sum(1 for e in events if e["event"] == "RESOURCE_CONSUMED")
    birth_events = [e for e in events if e["event"] == "BIRTH"]
    time_to_first_birth = birth_events[0]["tick"] if birth_events else None
    max_generation = max((int(e.get("generation", 0)) for e in birth_events), default=0)
    child_ids = {e["child_id"] for e in birth_events}
    founders_reproducing = len({e["parent_id"] for e in birth_events if e["parent_id"] not in child_ids})
    actions = Counter(e["action"] for e in events if e["event"] == "ACTION")
    invalid = sum(1 for e in events if e["event"] == "INVALID_ACTION")
    memory_writes = sum(1 for e in events if e["event"] == "MEMORY_WRITE")
    llm_calls = [e for e in events if e["event"] == "LLM_CALL"]
    llm_latencies = [
        float(e["latency_ms"]) for e in llm_calls if e.get("latency_ms") is not None
    ]
    populations = [e.get("population", 0) for e in tick_rows]
    energies = [e.get("total_energy", 0) for e in tick_rows]
    time_to_extinction = None
    for row in tick_rows:
        if row.get("population", 0) == 0:
            time_to_extinction = row["tick"] + 1
            break
    total_actions = sum(actions.values())
    probs = [count / total_actions for count in actions.values()] if total_actions else []
    action_entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    final_pop = populations[-1] if populations else 0
    return {
        "ticks": len(tick_rows),
        "final_population": final_pop,
        "mean_population": _mean([float(v) for v in populations]),
        "births": births,
        "deaths": deaths,
        "birth_rate": births / len(tick_rows) if tick_rows else 0.0,
        "death_rate": deaths / len(tick_rows) if tick_rows else 0.0,
        "time_to_extinction": time_to_extinction,
        "time_to_first_birth": time_to_first_birth,
        "max_generation": max_generation,
        "founders_reproducing_count": founders_reproducing,
        "mean_energy": _mean(
            [
                float(e["total_energy"]) / e["population"]
                for e in tick_rows
                if e.get("population")
            ]
        ),
        "energy_variance": _sd(
            [
                float(e["total_energy"]) / e["population"]
                for e in tick_rows
                if e.get("population")
            ]
        )
        ** 2,
        "total_energy_final": energies[-1] if energies else 0,
        "resources_consumed_count": consumed,
        "action_distribution": dict(actions),
        "action_entropy": action_entropy,
        "invalid_action_rate": invalid / total_actions if total_actions else 0.0,
        "llm_calls": len(llm_calls),
        "llm_mean_latency_ms": _mean(llm_latencies) if llm_latencies else 0.0,
        "memory_writes": memory_writes,
    }


def metrics_from_run(run_dir: str | Path) -> dict[str, Any]:
    events = read_events(Path(run_dir) / "events.jsonl")
    metrics = metrics_from_events(events)
    metrics["run_dir"] = str(run_dir)
    return metrics


def write_metrics_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    if not rows:
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in rows for key in row if key != "action_distribution"})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in keys})

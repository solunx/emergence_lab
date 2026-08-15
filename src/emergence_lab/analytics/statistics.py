"""Paired-by-seed comparisons. No intelligence score."""

from __future__ import annotations

import math
from dataclasses import dataclass


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def median(values: list[float]) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2


def sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def ci95(values: list[float]) -> tuple[float, float]:
    if len(values) < 2:
        m = mean(values)
        return m, m
    m = mean(values)
    err = 1.96 * sd(values) / math.sqrt(len(values))
    return m - err, m + err


def cohens_d(a: list[float], b: list[float]) -> float:
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled = math.sqrt((sd(a) ** 2 + sd(b) ** 2) / 2)
    if pooled == 0:
        return 0.0
    return (mean(a) - mean(b)) / pooled


@dataclass
class PairedDelta:
    metric: str
    a: str
    b: str
    deltas: list[float]

    @property
    def mean_delta(self) -> float:
        return mean(self.deltas)

    @property
    def median_delta(self) -> float:
        return median(self.deltas)

    def summary(self) -> dict:
        lo, hi = ci95(self.deltas)
        spread = sd(self.deltas)
        if not self.deltas:
            paired_d = float("nan")
        elif spread == 0:
            paired_d = 0.0
        else:
            paired_d = self.mean_delta / spread
        return {
            "metric": self.metric,
            "a": self.a,
            "b": self.b,
            "n": len(self.deltas),
            "mean_delta": self.mean_delta,
            "median_delta": self.median_delta,
            "sd_delta": spread,
            "ci95_lo": lo,
            "ci95_hi": hi,
            "cohens_d_paired": paired_d,
            "n_pos": sum(1 for d in self.deltas if d > 0),
            "n_zero": sum(1 for d in self.deltas if d == 0),
            "n_neg": sum(1 for d in self.deltas if d < 0),
        }


def _as_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def paired_deltas(
    rows: list[dict],
    metric: str,
    a: str,
    b: str,
    seed_key: str = "seed",
    controller_key: str = "controller",
) -> PairedDelta:
    by_seed: dict[int, dict[str, float]] = {}
    for row in rows:
        parsed = _as_float(row.get(metric))
        if parsed is None:
            continue
        seed = row[seed_key]
        controller = row[controller_key]
        by_seed.setdefault(seed, {})[controller] = parsed
    deltas = []
    for seed, mapping in sorted(by_seed.items()):
        if a in mapping and b in mapping:
            deltas.append(mapping[a] - mapping[b])
    return PairedDelta(metric=metric, a=a, b=b, deltas=deltas)

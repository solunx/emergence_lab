"""C1 vs C2-feature representability. Diagnostic only; not a matrix condition."""

from __future__ import annotations

import random
from collections import defaultdict

from emergence_lab.controllers.evolutionary import (
    EvolutionaryOracleController,
    extract_features,
)
from emergence_lab.controllers.reactive import ReactiveController
from emergence_lab.world.observation import Observation
from emergence_lab.world.types import ALL_ACTIONS, CellKind

RADIUS = 2
SIZE = 2 * RADIUS + 1
CENTER = RADIUS


def make_patch(*resources: tuple[int, int]) -> Observation:
    """Build a 5×5 observation. Offsets are (drow, dcol) from center; negative row is north."""
    rows: list[list[CellKind]] = [
        [CellKind.EMPTY for _ in range(SIZE)] for _ in range(SIZE)
    ]
    rows[CENTER][CENTER] = CellKind.SELF
    for drow, dcol in resources:
        row = CENTER + drow
        col = CENTER + dcol
        if not (0 <= row < SIZE and 0 <= col < SIZE):
            raise ValueError(f"offset {(drow, dcol)} outside 5×5")
        if row == CENTER and col == CENTER:
            raise ValueError("cannot place resource on SELF")
        rows[row][col] = CellKind.RESOURCE
    frozen = tuple(tuple(line) for line in rows)
    return Observation(energy=100, age=0, cells=frozen, available_actions=ALL_ACTIONS)


def resource_visibility(observation: Observation) -> str:
    """empty | on_axis | diagonal_only. on_axis may also contain extra diagonal food."""
    features = extract_features(observation)
    on_axis = any(features[i] > 0 for i in range(4))
    has_food = any(
        cell is CellKind.RESOURCE
        for r, line in enumerate(observation.cells)
        for c, cell in enumerate(line)
        if not (r == CENTER and c == CENTER)
    )
    if not has_food:
        return "empty"
    if on_axis:
        return "on_axis"
    return "diagonal_only"


def single_food_offsets() -> list[tuple[int, int]]:
    offsets = []
    for drow in range(-RADIUS, RADIUS + 1):
        for dcol in range(-RADIUS, RADIUS + 1):
            if drow == 0 and dcol == 0:
                continue
            offsets.append((drow, dcol))
    return offsets


def agreement_table(repeats: int = 20, rng_seed: int = 1) -> dict[str, dict[str, float]]:
    """C1 vs cardinal oracle on every single-food 5×5, plus empty patch."""
    c1 = ReactiveController(random.Random(rng_seed))
    oracle = EvolutionaryOracleController(random.Random(rng_seed + 1))
    buckets: dict[str, list[int]] = defaultdict(list)
    cases = [(make_patch(), "empty")]
    for offset in single_food_offsets():
        obs = make_patch(offset)
        cases.append((obs, resource_visibility(obs)))
    for obs, label in cases:
        for step in range(repeats):
            c1.rng.seed(rng_seed + step * 17)
            oracle.rng.seed(rng_seed + step * 31)
            match = int(c1.decide(obs).action is oracle.decide(obs).action)
            buckets[label].append(match)
            buckets["all"].append(match)
    out = {}
    for key, values in buckets.items():
        out[key] = {
            "n": float(len(values)),
            "agreement": sum(values) / len(values),
        }
    return out


def render_report(repeats: int = 20) -> str:
    table = agreement_table(repeats=repeats)
    empty = make_patch()
    diag = make_patch((-1, 1))
    north = make_patch((-1, 0))
    lines = [
        "# C2 representability (diagnostic)",
        "",
        "Same raw 5×5. C1 uses full Manhattan nearest-food. C2/oracle uses 8 cardinal bits + bias.",
        "Diagonal-only food is invisible to C2 features (identical to empty). Distance N1 vs N2 is one bit.",
        "The cardinal oracle is a hand-set genome, not evolved C2. Do not expand C2 features because C2 failed.",
        "",
        f"- empty patch resource bits: `{extract_features(empty)[:4]}`",
        f"- food NE `(-1,1)` resource bits: `{extract_features(diag)[:4]}` class=`{resource_visibility(diag)}`",
        f"- food N `(-1,0)` resource bits: `{extract_features(north)[:4]}` class=`{resource_visibility(north)}`",
        "",
        f"C1 vs cardinal oracle agreement ({repeats} RNG draws per patch):",
        "",
        "| Patch class | n | Agreement |",
        "|---|---:|---:|",
    ]
    for key in ("empty", "diagonal_only", "on_axis", "all"):
        row = table[key]
        lines.append(f"| {key} | {int(row['n'])} | {row['agreement']:.1%} |")
    lines.append("")
    lines.append(
        "On-axis should be high (oracle encodes C1’s cardinal step). "
        "Diagonal-only should be near chance (~20%): C1 walks toward the food, oracle sees no resource bit."
    )
    lines.append("")
    return "\n".join(lines)

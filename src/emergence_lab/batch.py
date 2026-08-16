"""Parse seed lists and decide which seed folders are already done."""

from __future__ import annotations

from pathlib import Path


def parse_seed_spec(spec: str) -> list[int]:
    """Parse '1-100', '1,5,9', or '1-3,10,20-21' into unique ordered ints."""
    seeds: list[int] = []
    for raw in spec.split(","):
        part = raw.strip()
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            try:
                lo = int(left.strip())
                hi = int(right.strip())
            except ValueError as exc:
                raise ValueError(f"invalid seed range {part!r}") from exc
            if hi < lo:
                raise ValueError(f"seed range {part!r} has end < start")
            seeds.extend(range(lo, hi + 1))
            continue
        try:
            seeds.append(int(part))
        except ValueError as exc:
            raise ValueError(f"invalid seed {part!r}") from exc
    if not seeds:
        raise ValueError("seed spec is empty")
    seen: set[int] = set()
    unique: list[int] = []
    for seed in seeds:
        if seed not in seen:
            seen.add(seed)
            unique.append(seed)
    return unique


def parse_controllers(spec: str) -> list[str]:
    names = [item.strip() for item in spec.split(",") if item.strip()]
    if not names:
        raise ValueError("controller list is empty")
    return names


def seed_is_complete(seed_dir: str | Path) -> bool:
    return (Path(seed_dir) / "metrics.csv").is_file()

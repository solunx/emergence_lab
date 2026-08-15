from __future__ import annotations

import json
from pathlib import Path

from emergence_lab.world.world import WorldState


def write_snapshot(path: str | Path, state: WorldState) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(state.to_dict(), handle, sort_keys=True, indent=2)


def read_snapshot(path: str | Path) -> WorldState:
    with Path(path).open("r", encoding="utf-8") as handle:
        return WorldState.from_dict(json.load(handle))

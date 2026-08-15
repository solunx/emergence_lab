from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, TextIO


@dataclass(frozen=True)
class Event:
    kind: str
    tick: int
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = {"event": self.kind, "tick": self.tick}
        data.update(self.payload)
        return data


class EventLog:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, kind: str, tick: int, **payload: Any) -> None:
        self.events.append(Event(kind=kind, tick=tick, payload=payload))

    def write_jsonl(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            write_events(handle, self.events)

    def sha256(self) -> str:
        import hashlib

        blob = "\n".join(
            json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":"))
            for event in self.events
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def write_events(handle: TextIO, events: Iterable[Event]) -> None:
    for event in events:
        handle.write(json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":")))
        handle.write("\n")


def read_events(path: str | Path) -> list[dict[str, Any]]:
    records = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

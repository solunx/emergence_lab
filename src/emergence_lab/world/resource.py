from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResourceSite:
    x: int
    y: int
    has_food: bool = True
    last_consumed_tick: int = 0

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "has_food": self.has_food,
            "last_consumed_tick": self.last_consumed_tick,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ResourceSite:
        return cls(
            x=data["x"],
            y=data["y"],
            has_food=data["has_food"],
            last_consumed_tick=data["last_consumed_tick"],
        )

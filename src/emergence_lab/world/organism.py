from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Organism:
    id: int
    x: int
    y: int
    energy: int
    age: int = 0
    alive: bool = True
    parent_id: int | None = None
    generation: int = 0
    controller_condition: str = "random"
    genome: tuple[float, ...] | None = None
    memory: list[str] = field(default_factory=list)

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "energy": self.energy,
            "age": self.age,
            "alive": self.alive,
            "parent_id": self.parent_id,
            "generation": self.generation,
            "controller_condition": self.controller_condition,
            "genome": list(self.genome) if self.genome is not None else None,
            "memory": list(self.memory),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Organism:
        genome = data.get("genome")
        return cls(
            id=data["id"],
            x=data["x"],
            y=data["y"],
            energy=data["energy"],
            age=data["age"],
            alive=data["alive"],
            parent_id=data.get("parent_id"),
            generation=data.get("generation", 0),
            controller_condition=data.get("controller_condition", "random"),
            genome=tuple(genome) if genome is not None else None,
            memory=list(data.get("memory") or []),
        )

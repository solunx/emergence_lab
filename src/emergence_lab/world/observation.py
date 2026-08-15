from __future__ import annotations

from dataclasses import dataclass

from emergence_lab.world.types import ALL_ACTIONS, Action, CellKind


@dataclass(frozen=True)
class Observation:
    energy: int
    age: int
    cells: tuple[tuple[CellKind, ...], ...]
    available_actions: tuple[Action, ...] = ALL_ACTIONS

    def to_dict(self) -> dict:
        return {
            "energy": self.energy,
            "age": self.age,
            "cells": [[cell.value for cell in row] for row in self.cells],
            "available_actions": [action.value for action in self.available_actions],
        }

    def ascii(self) -> str:
        glyphs = {
            CellKind.EMPTY: ".",
            CellKind.RESOURCE: "F",
            CellKind.ORGANISM: "O",
            CellKind.SELF: "A",
        }
        return "\n".join(" ".join(glyphs[cell] for cell in row) for row in self.cells)

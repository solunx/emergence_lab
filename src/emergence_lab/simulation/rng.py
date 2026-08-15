"""Separated RNG streams and stable conflict hashes. Never use Python hash()."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass


def seed_derived(seed: int, namespace: str) -> int:
    material = f"{seed}:{namespace}".encode("ascii")
    digest = hashlib.sha256(material).digest()
    return int.from_bytes(digest[:8], "big")


def conflict_winner(seed: int, tick: int, x: int, y: int, ids: list[int]) -> int:
    ids_sorted = sorted(ids)
    material = f"{seed}:{tick}:{x}:{y}:{','.join(map(str, ids_sorted))}"
    digest = hashlib.sha256(material.encode("ascii")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(ids_sorted)
    return ids_sorted[idx]


def pick_index(seed: int, tick: int, parent_id: int, n: int) -> int:
    if n <= 0:
        raise ValueError("n must be positive")
    material = f"{seed}:{tick}:{parent_id}:birth:{n}"
    digest = hashlib.sha256(material.encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big") % n


@dataclass
class RNGBundle:
    seed: int
    world: random.Random
    evolution: random.Random
    controller: random.Random

    @classmethod
    def from_seed(cls, seed: int) -> RNGBundle:
        return cls(
            seed=seed,
            world=random.Random(seed_derived(seed, "world")),
            evolution=random.Random(seed_derived(seed, "evolution")),
            controller=random.Random(seed_derived(seed, "controller")),
        )

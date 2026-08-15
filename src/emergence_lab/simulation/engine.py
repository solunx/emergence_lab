"""Simultaneous tick engine. Controllers never receive a World object."""

from __future__ import annotations

from collections import defaultdict

from emergence_lab.config import DECISION_CONTROLLER, SimConfig
from emergence_lab.controllers.base import Controller, Decision
from emergence_lab.controllers.evolutionary import EvolutionaryController, mutate_genome
from emergence_lab.controllers.random import RandomController
from emergence_lab.controllers.reactive import ReactiveController
from emergence_lab.controllers.verification import AlwaysNorthController, AlwaysStayController
from emergence_lab.simulation.events import EventLog
from emergence_lab.simulation.rng import RNGBundle, conflict_winner, pick_index
from emergence_lab.world.invariants import assert_invariants
from emergence_lab.world.organism import Organism
from emergence_lab.world.types import ALL_ACTIONS, Action
from emergence_lab.world.world import WorldState


def make_controller(name: str, rng_bundle: RNGBundle) -> Controller:
    mapping: dict[str, type[Controller]] = {
        "random": RandomController,
        "reactive": ReactiveController,
        "evolutionary": EvolutionaryController,
        "always_stay": AlwaysStayController,
        "always_north": AlwaysNorthController,
    }
    decision = DECISION_CONTROLLER.get(name, name)
    if decision not in mapping:
        raise ValueError(f"unknown controller: {name}")
    cls = mapping[decision]
    if decision in {"always_stay", "always_north"}:
        return cls()
    return cls(rng_bundle.controller)  # type: ignore[call-arg]


class Engine:
    def __init__(
        self,
        state: WorldState,
        rng: RNGBundle,
        controller: Controller,
        *,
        check_invariants: bool = False,
    ) -> None:
        self.state = state
        self.rng = rng
        self.controller = controller
        self.config: SimConfig = state.config
        self.log = EventLog()
        self.check_invariants = check_invariants
        self.founders = len(state.organisms)
        self.births = 0
        self.deaths = 0
        self._pending_memory: dict[int, str] = {}

    def run(self, ticks: int) -> EventLog:
        if self.check_invariants:
            assert_invariants(self.state)
        self.log.emit("TICK_STARTED", 0, phase="initial")
        self.log.emit(
            "TICK_FINISHED",
            0,
            population=len(self.state.living()),
            phase="initial",
        )
        for tick in range(ticks):
            self.step(tick)
        return self.log

    def step(self, tick: int) -> None:
        state = self.state
        state.tick = tick
        self.log.emit("TICK_STARTED", tick)
        self._regen(tick)
        living = state.living()
        observations = {org.id: state.observe(org) for org in living}
        decisions: dict[int, Decision] = {}
        for org in living:
            obs = observations[org.id]
            self.log.emit("OBSERVATION", tick, organism_id=org.id, observation=obs.to_dict())
            genome = org.genome if self.config.genome_enabled else None
            memory = list(org.memory) if org.memory else None
            decision = self.controller.decide(obs, genome=genome, memory=memory)
            decisions[org.id] = decision

        intended: dict[int, tuple[int, int]] = {}
        moved: dict[int, bool] = {}
        for org in living:
            decision = decisions[org.id]
            action = decision.action
            valid = action in ALL_ACTIONS
            if not valid:
                self.log.emit(
                    "INVALID_ACTION",
                    tick,
                    organism_id=org.id,
                    raw=str(action),
                    fallback="STAY",
                )
                action = Action.STAY
            self.log.emit("ACTION", tick, organism_id=org.id, action=action.value)
            if decision.memory_write:
                self.log.emit(
                    "MEMORY_WRITE",
                    tick,
                    organism_id=org.id,
                    text=decision.memory_write,
                )
                self._pending_memory[org.id] = decision.memory_write
            if action is Action.STAY:
                intended[org.id] = (org.x, org.y)
                moved[org.id] = False
            else:
                intended[org.id] = state.destination(org.x, org.y, action)
                moved[org.id] = True

        occupied_at_t = {(org.x, org.y) for org in living}
        winners, blocked = self._resolve_movement(tick, living, intended, occupied_at_t)

        consumed_ids: set[int] = set()
        for org in living:
            if org.id in winners:
                dest = intended[org.id]
                origin = (org.x, org.y)
                del state.occupied[origin]
                org.x, org.y = dest
                state.occupied[dest] = org.id
                self.log.emit(
                    "MOVE",
                    tick,
                    organism_id=org.id,
                    **{"from": list(origin), "to": list(dest)},
                )
            elif org.id in blocked:
                moved[org.id] = False

        for org in living:
            if org.position in state.food:
                self._consume(tick, org)
                consumed_ids.add(org.id)

        for org in living:
            if not org.alive:
                continue
            cost = self.config.base_metabolism
            if org.id in winners:
                cost += self.config.movement_cost
            org.energy -= cost

        newly_dead: list[Organism] = []
        for org in living:
            if org.energy <= 0:
                org.alive = False
                org.energy = 0
                newly_dead.append(org)
        for org in newly_dead:
            state.occupied.pop((org.x, org.y), None)
            self.deaths += 1
            self.log.emit("DEATH", tick, organism_id=org.id, x=org.x, y=org.y)

        if self.config.reproduction_enabled:
            self._reproduce(tick)

        for org in state.living():
            org.age += 1

        self._apply_memory_writes()

        if self.check_invariants:
            assert_invariants(state)
            living_count = len(state.living())
            expected = self.founders + self.births - self.deaths
            if living_count != expected:
                raise AssertionError(
                    f"population accounting failed: {living_count} != {expected}"
                )

        action_counts: dict[str, int] = defaultdict(int)
        for org_id, decision in decisions.items():
            action = decision.action if decision.action in ALL_ACTIONS else Action.STAY
            if org_id not in winners and moved.get(org_id):
                action = Action.STAY
            action_counts[action.value] += 1
        self.log.emit(
            "TICK_FINISHED",
            tick,
            population=len(state.living()),
            total_energy=sum(org.energy for org in state.living()),
            resources_present=len(state.food),
            births=self.births,
            deaths=self.deaths,
            action_counts=dict(action_counts),
        )
        state.tick = tick + 1

    def _regen(self, tick: int) -> None:
        delay = self.config.regen_delay
        for site in self.state.sites:
            pos = (site.x, site.y)
            if site.has_food:
                continue
            if pos in self.state.occupied:
                continue
            if tick - site.last_consumed_tick >= delay:
                site.has_food = True
                self.state.food.add(pos)
                self.log.emit("RESOURCE_REGEN", tick, x=site.x, y=site.y)

    def _consume(self, tick: int, org: Organism) -> None:
        pos = org.position
        site = self.state.site_index[pos]
        if not site.has_food:
            return
        site.has_food = False
        site.last_consumed_tick = tick
        self.state.food.discard(pos)
        org.energy += self.config.resource_value
        self.log.emit(
            "RESOURCE_CONSUMED",
            tick,
            organism_id=org.id,
            x=pos[0],
            y=pos[1],
            value=self.config.resource_value,
        )

    def _resolve_movement(
        self,
        tick: int,
        living: list[Organism],
        intended: dict[int, tuple[int, int]],
        occupied_at_t: set[tuple[int, int]],
    ) -> tuple[set[int], set[int]]:
        winners: set[int] = set()
        blocked: set[int] = set()
        claims: dict[tuple[int, int], list[int]] = defaultdict(list)
        by_id = {org.id: org for org in living}
        for org in living:
            dest = intended[org.id]
            if dest == (org.x, org.y):
                continue
            if dest in occupied_at_t:
                blocked.add(org.id)
                self.log.emit(
                    "MOVE_BLOCKED",
                    tick,
                    organism_id=org.id,
                    **{"from": list(org.position), "to": list(dest)},
                    reason="occupied",
                )
                continue
            claims[dest].append(org.id)

        for dest, pretenders in claims.items():
            if len(pretenders) == 1:
                winners.add(pretenders[0])
                continue
            winner = conflict_winner(self.state.seed, tick, dest[0], dest[1], pretenders)
            winners.add(winner)
            self.log.emit(
                "MOVE_CONFLICT",
                tick,
                x=dest[0],
                y=dest[1],
                pretenders=sorted(pretenders),
                winner=winner,
            )
            for pid in pretenders:
                if pid != winner:
                    blocked.add(pid)
                    org = by_id[pid]
                    self.log.emit(
                        "MOVE_BLOCKED",
                        tick,
                        organism_id=pid,
                        **{"from": list(org.position), "to": list(dest)},
                        reason="conflict",
                    )
        return winners, blocked

    def _reproduce(self, tick: int) -> None:
        state = self.state
        cfg = self.config
        parents = [org for org in state.living() if org.energy >= cfg.reproduction_energy_threshold]
        if not parents:
            return
        choices: list[tuple[Organism, tuple[int, int]]] = []
        for parent in sorted(parents, key=lambda o: o.id):
            empty: list[tuple[int, int]] = []
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nx, ny = state.wrap_xy(parent.x + dx, parent.y + dy)
                if (nx, ny) not in state.occupied:
                    empty.append((nx, ny))
            if not empty:
                continue
            idx = pick_index(state.seed, tick, parent.id, len(empty))
            choices.append((parent, empty[idx]))

        by_cell: dict[tuple[int, int], list[Organism]] = defaultdict(list)
        for parent, cell in choices:
            by_cell[cell].append(parent)

        for cell, claimants in by_cell.items():
            if len(claimants) == 1:
                winner = claimants[0]
            else:
                winner_id = conflict_winner(
                    state.seed, tick, cell[0], cell[1], [p.id for p in claimants]
                )
                winner = next(p for p in claimants if p.id == winner_id)
            if cell in state.occupied:
                continue
            self._spawn(tick, winner, cell)

    def _spawn(self, tick: int, parent: Organism, cell: tuple[int, int]) -> None:
        state = self.state
        cfg = self.config
        parent.energy -= cfg.reproduction_cost
        genome = None
        if cfg.genome_enabled:
            if parent.genome is None:
                raise ValueError("parent missing genome")
            genome = mutate_genome(
                parent.genome,
                self.rng.evolution,
                cfg.mutation_probability,
                cfg.mutation_strength,
            )
        child = Organism(
            id=state.next_organism_id,
            x=cell[0],
            y=cell[1],
            energy=cfg.reproduction_cost,
            age=0,
            alive=True,
            parent_id=parent.id,
            generation=parent.generation + 1,
            controller_condition=parent.controller_condition,
            genome=genome,
            memory=[],
        )
        state.next_organism_id += 1
        state.organisms.append(child)
        state.occupied[cell] = child.id
        self.births += 1
        self.log.emit(
            "BIRTH",
            tick,
            parent_id=parent.id,
            child_id=child.id,
            x=cell[0],
            y=cell[1],
            parent_energy=parent.energy,
            child_energy=child.energy,
            generation=child.generation,
        )
        if cell in state.food:
            self._consume(tick, child)

    def _apply_memory_writes(self) -> None:
        cap = self.config.memory_capacity
        max_chars = self.config.memory_entry_max_chars
        for organism_id, text in self._pending_memory.items():
            org = self.state.organism_by_id(organism_id)
            if not org.alive:
                continue
            entry = text[:max_chars]
            if not entry:
                continue
            org.memory.append(entry)
            if len(org.memory) > cap:
                org.memory = org.memory[-cap:]
        self._pending_memory.clear()

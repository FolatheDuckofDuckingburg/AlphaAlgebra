"""Deterministic bounded breadth-first search over verified algebra steps."""

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Hashable

from alphaalgebra.core.proof_state import ProofState, TransformationStep
from alphaalgebra.rules.registry import RuleRegistry
from alphaalgebra.problem.goals import Goal
from .candidates import CandidateRejection, generate_candidates


class SearchStatus(str, Enum):
    """Terminal outcome of a bounded symbolic search."""

    SOLVED = "solved"
    FRONTIER_EXHAUSTED = "frontier_exhausted"
    DEPTH_LIMIT_REACHED = "depth_limit_reached"
    NODE_BUDGET_EXHAUSTED = "node_budget_exhausted"


@dataclass(frozen=True, slots=True)
class SearchResult:
    """A search outcome with a replayable proof path and budget accounting."""

    status: SearchStatus
    proof: tuple[TransformationStep, ...]
    expanded_nodes: int
    discovered_states: int
    deepest_level: int
    rejected_candidates: tuple[CandidateRejection, ...]

    @property
    def solved(self) -> bool:
        return self.status is SearchStatus.SOLVED


StateKey = Callable[[ProofState], Hashable]
GoalPredicate = Callable[[ProofState], bool]


def _default_state_key(state: ProofState) -> str:
    """Use the immutable AST representation as a deterministic initial key."""
    return repr(state)


def bounded_symbolic_search(
    initial_state: ProofState,
    goal: Goal | GoalPredicate,
    registry: RuleRegistry,
    *,
    max_depth: int = 8,
    max_expanded_nodes: int = 1_000,
    state_key: StateKey | None = None,
) -> SearchResult:
    """Run deterministic breadth-first search using only verified transitions.

    Every edge is produced by generate_candidates, which checks source-state
    identity and invokes the registry's independent checker. The goal predicate
    is supplied by the caller; this function does not infer mathematical goals.

    max_depth counts transitions from the initial state. The node budget counts
    states for which candidate generation is attempted. Search is not complete
    beyond the supplied limits, and no theorem-solving completeness is claimed.
    """
    if not isinstance(initial_state, ProofState):
        raise TypeError("initial_state must be a ProofState")
    if callable(goal):
        goal_fn = goal
    elif callable(getattr(goal, "is_satisfied", None)):
        goal_fn = goal.is_satisfied
    else:
        raise TypeError("goal must be callable or implement is_satisfied(state)")
    if not isinstance(registry, RuleRegistry):
        raise TypeError("registry must be a RuleRegistry")
    for name, value in (("max_depth", max_depth), ("max_expanded_nodes", max_expanded_nodes)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    key_fn = _default_state_key if state_key is None else state_key
    if not callable(key_fn):
        raise TypeError("state_key must be callable")

    initial_key = key_fn(initial_state)
    try:
        hash(initial_key)
    except TypeError as exc:
        raise TypeError("state_key must return a hashable value") from exc
    if goal_fn(initial_state):
        return SearchResult(SearchStatus.SOLVED, (), 0, 1, 0, ())

    frontier = deque([(initial_state, (), 0)])
    seen: set[Hashable] = {initial_key}
    expanded = 0
    deepest = 0
    depth_limited = False
    rejected: list[CandidateRejection] = []

    while frontier:
        state, path, depth = frontier.popleft()
        deepest = max(deepest, depth)

        if depth >= max_depth:
            depth_limited = True
            continue
        if expanded >= max_expanded_nodes:
            return SearchResult(
                SearchStatus.NODE_BUDGET_EXHAUSTED,
                (),
                expanded,
                len(seen),
                deepest,
                tuple(rejected),
            )

        expanded += 1
        generated = generate_candidates(state, registry)
        rejected.extend(generated.rejected)

        for step in generated.candidates:
            next_state = step.after
            next_key = key_fn(next_state)
            try:
                hash(next_key)
            except TypeError as exc:
                raise TypeError("state_key must return a hashable value") from exc
            next_path = path + (step,)
            next_depth = depth + 1
            deepest = max(deepest, next_depth)
            if goal_fn(next_state):
                return SearchResult(
                    SearchStatus.SOLVED,
                    next_path,
                    expanded,
                    len(seen) + (0 if next_key in seen else 1),
                    deepest,
                    tuple(rejected),
                )
            if next_key in seen:
                continue
            seen.add(next_key)
            frontier.append((next_state, next_path, next_depth))

    status = SearchStatus.DEPTH_LIMIT_REACHED if depth_limited else SearchStatus.FRONTIER_EXHAUSTED
    return SearchResult(status, (), expanded, len(seen), deepest, tuple(rejected))

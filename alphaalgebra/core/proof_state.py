"""Immutable proof-state and transformation-step records.

These records describe proposed transitions. They do not establish that a
transition is mathematically valid; verification is a separate responsibility.
"""
from dataclasses import dataclass, field
from enum import Enum

from .assumptions import Assumptions
from .relations import Relation


class RelationSemantics(str, Enum):
    """Logical relationship asserted between a step's before and after states."""

    EQUIVALENCE = "equivalence"
    FORWARD_IMPLICATION = "forward_implication"
    REVERSE_IMPLICATION = "reverse_implication"


@dataclass(frozen=True, slots=True)
class ProofState:
    """A finite collection of relations under explicit symbol assumptions."""

    relations: tuple[Relation, ...]
    assumptions: Assumptions = field(default_factory=Assumptions)

    def __post_init__(self) -> None:
        if not isinstance(self.relations, tuple):
            object.__setattr__(self, "relations", tuple(self.relations))
        if not all(isinstance(item, Relation) for item in self.relations):
            raise TypeError("ProofState.relations must contain Relation values")
        if not isinstance(self.assumptions, Assumptions):
            raise TypeError("ProofState.assumptions must be an Assumptions value")


@dataclass(frozen=True, slots=True)
class TransformationStep:
    """A proposed state transition with explicit rule and logical metadata.

    Side-condition strings are identifiers/descriptions only. This data model
    does not parse, infer, or verify them.
    """

    rule_id: str
    before: ProofState
    after: ProofState
    semantics: RelationSemantics
    side_conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, str) or not self.rule_id.strip():
            raise ValueError("rule_id must be a non-empty string")
        if not isinstance(self.before, ProofState) or not isinstance(self.after, ProofState):
            raise TypeError("before and after must be ProofState values")
        if not isinstance(self.semantics, RelationSemantics):
            raise TypeError("semantics must be a RelationSemantics value")
        if not isinstance(self.side_conditions, tuple):
            object.__setattr__(self, "side_conditions", tuple(self.side_conditions))
        if any(not isinstance(item, str) or not item.strip() for item in self.side_conditions):
            raise ValueError("side_conditions must contain non-empty strings")

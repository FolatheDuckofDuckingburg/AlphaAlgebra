"""Typed, inspectable goal specifications for supported algebra problems."""

from dataclasses import dataclass
from typing import Protocol

from alphaalgebra.core.ast import Rational, Symbol
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation


class Goal(Protocol):
    """A mathematical objective that can be evaluated against a proof state."""

    def is_satisfied(self, state: ProofState) -> bool:
        """Return whether the state establishes this goal."""


@dataclass(frozen=True, slots=True)
class EquationSolutionGoal:
    """Goal asserting that one variable has one exact rational solution."""

    variable: str
    value: Rational

    def __post_init__(self) -> None:
        if not isinstance(self.variable, str) or not self.variable.strip():
            raise ValueError("variable must be a non-empty string")
        if not isinstance(self.value, Rational):
            raise TypeError("value must be a Rational expression")

    def is_satisfied(self, state: ProofState) -> bool:
        if not isinstance(state, ProofState) or len(state.relations) != 1:
            return False
        relation = state.relations[0]
        return (
            isinstance(relation, Equation)
            and isinstance(relation.left, Symbol)
            and relation.left.name == self.variable
            and relation.right == self.value
        )

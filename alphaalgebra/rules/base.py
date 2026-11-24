"""Contracts for deterministic, versioned symbolic transformation rules."""

from typing import Protocol, runtime_checkable

from alphaalgebra.core.proof_state import ProofState, TransformationStep


@runtime_checkable
class TransformationRule(Protocol):
    """A deterministic rule that proposes a transition, never self-certifies it.

    The verifier is registered separately. A rule's output is only a proposal
    until an independent checker accepts the complete transition.
    """

    rule_id: str
    version: str

    def is_applicable(self, state: ProofState) -> bool:
        """Return whether the rule's syntactic matcher accepts this state."""

    def apply(self, state: ProofState) -> TransformationStep:
        """Propose a transition; callers must pass it to the verifier."""

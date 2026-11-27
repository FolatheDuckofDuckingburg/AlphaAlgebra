"""Conservative canonical keys for supported polynomial equation states."""

from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation
from alphaalgebra.core.transformations import normalize_polynomial_equation


def canonical_polynomial_state_key(state: ProofState) -> tuple:
    """Canonicalize supported polynomial equation syntax, preserving assumptions.

    Unsupported relations/equations fall back to structural representations.
    This does not identify scalar multiples or establish full equivalence.
    """
    if not isinstance(state, ProofState):
        raise TypeError("state must be a ProofState")
    assumptions_key = (
        tuple(sorted(state.assumptions.nonzero)),
        tuple(sorted(state.assumptions.positive)),
        tuple(sorted(state.assumptions.integer)),
    )
    relation_keys = []
    for relation in state.relations:
        if isinstance(relation, Equation):
            try:
                residual = normalize_polynomial_equation(relation).residual
            except (TypeError, ValueError, AttributeError):
                relation_keys.append(("structural", repr(relation)))
            else:
                relation_keys.append(("polynomial_equation", residual.terms))
        else:
            relation_keys.append(("structural", repr(relation)))
    return ("proof_state", assumptions_key, tuple(relation_keys))

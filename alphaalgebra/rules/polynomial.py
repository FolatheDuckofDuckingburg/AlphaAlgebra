"""Initial rule adapters for the supported polynomial fragment."""

from alphaalgebra.core.proof_state import ProofState, TransformationStep
from alphaalgebra.core.relations import Equation
from alphaalgebra.core.transformations import (
    RULE_POLYNOMIAL_EQUATION_TO_ZERO,
    apply_polynomial_equation_to_zero,
)


class PolynomialEquationToZeroRule:
    """Normalize one polynomial equation L = R into L - R = 0."""

    rule_id = RULE_POLYNOMIAL_EQUATION_TO_ZERO
    version = "1.0.0"

    def is_applicable(self, state: ProofState) -> bool:
        if not isinstance(state, ProofState) or len(state.relations) != 1:
            return False
        if not isinstance(state.relations[0], Equation):
            return False
        # Applicability includes membership in the supported polynomial AST.
        try:
            from alphaalgebra.core.polynomial import polynomial_from_expr
            equation = state.relations[0]
            polynomial_from_expr(equation.left)
            polynomial_from_expr(equation.right)
        except (TypeError, ValueError):
            return False
        return True

    def apply(self, state: ProofState) -> TransformationStep:
        if not self.is_applicable(state):
            raise ValueError("state is not applicable to polynomial_equation_to_zero")
        return apply_polynomial_equation_to_zero(state)


class RationalQuadraticFactorizationRule:
    """Factor a univariate rational-root quadratic equation exactly."""

    from alphaalgebra.core.transformations import RULE_FACTOR_RATIONAL_QUADRATIC as rule_id
    version = "1.0.0"

    def is_applicable(self, state: ProofState) -> bool:
        if not isinstance(state, ProofState) or len(state.relations) != 1:
            return False
        if not isinstance(state.relations[0], Equation):
            return False
        try:
            from alphaalgebra.core.transformations import (
                factor_rational_quadratic,
                normalize_polynomial_equation,
            )
            residual = normalize_polynomial_equation(state.relations[0]).residual
            return factor_rational_quadratic(residual) is not None
        except (TypeError, ValueError):
            return False

    def apply(self, state: ProofState) -> TransformationStep:
        if not self.is_applicable(state):
            raise ValueError("state is not applicable to rational quadratic factorization")
        from alphaalgebra.core.transformations import apply_rational_quadratic_factorization
        return apply_rational_quadratic_factorization(state)

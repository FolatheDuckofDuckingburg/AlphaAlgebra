"""Conservative, explicit transformations for polynomial equations.

The first rule maps L = R to the zero equation L - R = 0. This is an
equivalence-preserving normalization over the supported polynomial fragment;
it does not solve the equation or introduce cancellation/division rules.
"""
from dataclasses import dataclass

from .polynomial import Polynomial, polynomial_from_expr
from .relations import Equation


RULE_POLYNOMIAL_EQUATION_TO_ZERO = "polynomial_equation_to_zero"


@dataclass(frozen=True, slots=True)
class PolynomialEquationNormalForm:
    """Result of normalizing an equation to a polynomial equal to zero.

    The represented equation is residual = 0. The source equation and
    residual are retained so an independent checker can recompute the result.
    No assumptions or side conditions are needed for this rule.
    """

    source: Equation
    residual: Polynomial

    @property
    def rule_name(self) -> str:
        return RULE_POLYNOMIAL_EQUATION_TO_ZERO

    @property
    def relation(self) -> str:
        return "equivalent"

    @property
    def side_conditions(self) -> tuple[str, ...]:
        return ()


def polynomial_difference(left: Polynomial, right: Polynomial) -> Polynomial:
    """Return the exact canonical polynomial left - right."""
    if not isinstance(left, Polynomial) or not isinstance(right, Polynomial):
        raise TypeError("polynomial_difference expects two Polynomial values")
    negated_right = tuple(
        (monomial, -coefficient) for monomial, coefficient in right.terms
    )
    return Polynomial(left.terms + negated_right)


def normalize_polynomial_equation(
    equation: Equation,
) -> PolynomialEquationNormalForm:
    """Apply the equivalence-preserving rule L = R -> L - R = 0.

    Both sides must belong to the supported polynomial AST fragment. The
    operation performs no division, cancellation, factor removal, or solving.
    """
    if not isinstance(equation, Equation):
        raise TypeError("normalize_polynomial_equation expects an Equation")
    left = polynomial_from_expr(equation.left)
    right = polynomial_from_expr(equation.right)
    return PolynomialEquationNormalForm(
        source=equation,
        residual=polynomial_difference(left, right),
    )


def verify_polynomial_equation_normal_form(
    result: PolynomialEquationNormalForm,
) -> bool:
    """Independently recompute and check a normalization result.

    Returns False for malformed or tampered results. Unsupported source
    expressions are rejected by the normalizer and also fail verification.
    """
    if not isinstance(result, PolynomialEquationNormalForm):
        return False
    try:
        expected = normalize_polynomial_equation(result.source)
    except (TypeError, ValueError):
        return False
    return (
        result.rule_name == RULE_POLYNOMIAL_EQUATION_TO_ZERO
        and result.relation == "equivalent"
        and result.side_conditions == ()
        and result.residual == expected.residual
    )

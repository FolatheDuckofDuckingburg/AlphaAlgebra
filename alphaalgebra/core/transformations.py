"""Conservative, explicit transformations for polynomial equations.

The initial rule maps L = R to the zero equation L - R = 0. It is an
equivalence-preserving normalization over the supported polynomial fragment.
It does not solve equations or introduce division/cancellation rules.
"""
from dataclasses import dataclass

from .polynomial import Polynomial, polynomial_from_expr
from .relations import Equation

RULE_POLYNOMIAL_EQUATION_TO_ZERO = "polynomial_equation_to_zero"


@dataclass(frozen=True, slots=True)
class PolynomialEquationNormalForm:
    """A source equation and its exact polynomial residual, representing r = 0."""

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
    return Polynomial(
        left.terms
        + tuple((monomial, -coefficient) for monomial, coefficient in right.terms)
    )


def normalize_polynomial_equation(
    equation: Equation,
) -> PolynomialEquationNormalForm:
    """Convert L = R into the equivalent polynomial equation L - R = 0.

    Both sides must be in the supported polynomial AST fragment. This rule
    performs no division, cancellation, factor removal, or equation solving.
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
    """Recompute the named normalization and reject malformed/tampered output.

    This checker covers only this one normalization rule. It is not a
    general-purpose proof verifier and does not verify arbitrary derivations.
    """
    if not isinstance(result, PolynomialEquationNormalForm):
        return False
    try:
        expected = normalize_polynomial_equation(result.source)
    except (TypeError, ValueError, AttributeError):
        return False
    return (
        result.rule_name == RULE_POLYNOMIAL_EQUATION_TO_ZERO
        and result.relation == "equivalent"
        and result.side_conditions == ()
        and result.residual == expected.residual
    )

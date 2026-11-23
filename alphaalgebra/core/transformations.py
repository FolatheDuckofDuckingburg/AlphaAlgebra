"""Conservative, explicit transformations for polynomial equations.

The initial rule maps L = R to the zero equation L - R = 0. It is an
equivalence-preserving normalization over the supported polynomial fragment.
It does not solve equations or introduce division/cancellation rules.
"""
from dataclasses import dataclass

from .ast import Add, Expr, Multiply, Power, Rational, Symbol
from .polynomial import Polynomial, polynomial_from_expr
from .proof_state import ProofState, RelationSemantics, TransformationStep
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


def _polynomial_to_expr(polynomial: Polynomial) -> Expr:
    """Build a canonical AST expression from an exact sparse polynomial."""
    if not isinstance(polynomial, Polynomial):
        raise TypeError("polynomial must be a Polynomial")

    terms: list[Expr] = []
    for monomial, coefficient in polynomial.terms:
        factors: list[Expr] = []
        if coefficient != 1 or not monomial:
            factors.append(Rational(coefficient))
        for name, exponent in monomial:
            symbol = Symbol(name)
            factors.append(
                symbol if exponent == 1 else Power(symbol, Rational(exponent))
            )
        if not factors:
            term: Expr = Rational(1)
        elif len(factors) == 1:
            term = factors[0]
        else:
            term = Multiply(tuple(factors))
        terms.append(term)

    if not terms:
        return Rational(0)
    if len(terms) == 1:
        return terms[0]
    return Add(tuple(terms))


def apply_polynomial_equation_to_zero(state: ProofState) -> TransformationStep:
    """Apply the polynomial equation-to-zero rule to a one-equation state.

    The resulting state preserves the input assumptions. The rule is an
    equivalence over the supported polynomial fragment and has no side
    conditions because it uses only addition/subtraction, not division.
    """
    if not isinstance(state, ProofState):
        raise TypeError("state must be a ProofState")
    if len(state.relations) != 1 or not isinstance(state.relations[0], Equation):
        raise ValueError("the rule requires a state containing exactly one equation")

    normal_form = normalize_polynomial_equation(state.relations[0])
    after = ProofState(
        (Equation(_polynomial_to_expr(normal_form.residual), Rational(0)),),
        state.assumptions,
    )
    return TransformationStep(
        rule_id=RULE_POLYNOMIAL_EQUATION_TO_ZERO,
        before=state,
        after=after,
        semantics=RelationSemantics.EQUIVALENCE,
        side_conditions=(),
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


def verify_polynomial_equation_step(step: TransformationStep) -> bool:
    """Independently recompute and verify this rule's complete state transition.

    The checker accepts only the exact rule ID, equivalence semantics, empty
    side-condition set, one-equation input/output states, and unchanged
    assumptions. It does not verify other rules or general logical entailment.
    """
    if not isinstance(step, TransformationStep):
        return False
    if (
        step.rule_id != RULE_POLYNOMIAL_EQUATION_TO_ZERO
        or step.semantics is not RelationSemantics.EQUIVALENCE
        or step.side_conditions != ()
        or len(step.before.relations) != 1
        or not isinstance(step.before.relations[0], Equation)
    ):
        return False
    try:
        expected = apply_polynomial_equation_to_zero(step.before)
    except (TypeError, ValueError, AttributeError):
        return False
    return (
        step.after == expected.after
        and step.after.assumptions == step.before.assumptions
    )

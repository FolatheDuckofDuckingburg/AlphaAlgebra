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
        source_equation = step.before.relations[0]
        left = polynomial_from_expr(source_equation.left)
        right = polynomial_from_expr(source_equation.right)
        expected_residual = polynomial_difference(left, right)
        expected_after = ProofState(
            (Equation(_polynomial_to_expr(expected_residual), Rational(0)),),
            step.before.assumptions,
        )
    except (TypeError, ValueError, AttributeError):
        return False
    return step.after == expected_after


# Exact rational quadratic factorization. This deliberately supports only
# univariate quadratics whose discriminant has an exact rational square root.
RULE_FACTOR_RATIONAL_QUADRATIC = "factor_rational_quadratic"


def _rational_square_root(value):
    """Return the exact non-negative rational square root, or None."""
    from math import isqrt
    from fractions import Fraction

    exact = Fraction(value)
    if exact < 0:
        return None
    numerator_root = isqrt(exact.numerator)
    denominator_root = isqrt(exact.denominator)
    if numerator_root * numerator_root != exact.numerator:
        return None
    if denominator_root * denominator_root != exact.denominator:
        return None
    return Fraction(numerator_root, denominator_root)


def factor_rational_quadratic(polynomial: Polynomial) -> Expr | None:
    """Factor a univariate quadratic over Q when its roots are rational.

    Returns an exact expression equivalent to the polynomial, or None when
    the polynomial is outside this deliberately narrow factorization domain.
    """
    from fractions import Fraction

    if not isinstance(polynomial, Polynomial):
        raise TypeError("polynomial must be a Polynomial")

    coefficients = {0: Fraction(0), 1: Fraction(0), 2: Fraction(0)}
    variable = None
    for monomial, coefficient in polynomial.terms:
        if not monomial:
            coefficients[0] += coefficient
            continue
        if len(monomial) != 1:
            return None
        name, exponent = monomial[0]
        if exponent not in (1, 2):
            return None
        if variable is None:
            variable = name
        elif variable != name:
            return None
        coefficients[exponent] += coefficient

    a, b, c = coefficients[2], coefficients[1], coefficients[0]
    if not a or variable is None:
        return None

    discriminant_root = _rational_square_root(b * b - 4 * a * c)
    if discriminant_root is None:
        return None

    root_one = (-b + discriminant_root) / (2 * a)
    root_two = (-b - discriminant_root) / (2 * a)
    symbol = Symbol(variable)

    def linear_factor(root):
        return symbol if root == 0 else Add((symbol, Rational(-root)))

    factors: list[Expr] = [linear_factor(root_one), linear_factor(root_two)]
    if a != 1:
        factors.insert(0, Rational(a))
    if len(factors) == 1:
        return factors[0]
    return Multiply(tuple(factors))


def apply_rational_quadratic_factorization(
    state: ProofState,
) -> TransformationStep:
    """Factor the polynomial residual of a one-equation state over Q."""
    if not isinstance(state, ProofState):
        raise TypeError("state must be a ProofState")
    if len(state.relations) != 1 or not isinstance(state.relations[0], Equation):
        raise ValueError("factorization requires exactly one equation")
    normal_form = normalize_polynomial_equation(state.relations[0])
    factored = factor_rational_quadratic(normal_form.residual)
    if factored is None:
        raise ValueError("equation residual is not a supported rational-root quadratic")
    after = ProofState(
        (Equation(factored, Rational(0)),),
        state.assumptions,
    )
    return TransformationStep(
        rule_id=RULE_FACTOR_RATIONAL_QUADRATIC,
        before=state,
        after=after,
        semantics=RelationSemantics.EQUIVALENCE,
        side_conditions=(),
    )


def verify_rational_quadratic_factorization_step(step: TransformationStep) -> bool:
    """Independently recompute and check an exact rational quadratic factorization."""
    if not isinstance(step, TransformationStep):
        return False
    if (
        step.rule_id != RULE_FACTOR_RATIONAL_QUADRATIC
        or step.semantics is not RelationSemantics.EQUIVALENCE
        or step.side_conditions != ()
        or len(step.before.relations) != 1
        or not isinstance(step.before.relations[0], Equation)
    ):
        return False
    try:
        residual = normalize_polynomial_equation(step.before.relations[0]).residual
        expected_expression = factor_rational_quadratic(residual)
        if expected_expression is None:
            return False
        expected_after = ProofState(
            (Equation(expected_expression, Rational(0)),),
            step.before.assumptions,
        )
    except (TypeError, ValueError, AttributeError, ZeroDivisionError):
        return False
    return step.after == expected_after

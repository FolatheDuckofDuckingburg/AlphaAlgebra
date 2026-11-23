import unittest
from dataclasses import replace
from fractions import Fraction

from alphaalgebra.core.ast import Add, Multiply, Power, Rational, Symbol
from alphaalgebra.core.assumptions import Assumptions
from alphaalgebra.core.polynomial import Polynomial, UnsupportedPolynomialExpression
from alphaalgebra.core.proof_state import ProofState, RelationSemantics
from alphaalgebra.core.relations import Equation
from alphaalgebra.core.transformations import (
    RULE_POLYNOMIAL_EQUATION_TO_ZERO,
    apply_polynomial_equation_to_zero,
    normalize_polynomial_equation,
    polynomial_difference,
    verify_polynomial_equation_normal_form,
    verify_polynomial_equation_step,
)


class PolynomialEquationNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")
        self.y = Symbol("y")

    def test_equation_is_moved_to_zero_exactly(self):
        equation = Equation(Add((self.x, Rational(1))), Multiply((Rational(2), self.x)))
        result = normalize_polynomial_equation(equation)
        expected = Polynomial((
            ((), Fraction(1)),
            ((( "x", 1),), Fraction(-1)),
        ))
        self.assertEqual(result.residual, expected)
        self.assertEqual(result.source, equation)

    def test_equivalent_expanded_forms_have_zero_residual(self):
        left = Multiply((
            Add((self.x, Rational(1))),
            Add((self.x, Rational(-1))),
        ))
        right = Add((Power(self.x, Rational(2)), Rational(-1)))
        result = normalize_polynomial_equation(Equation(left, right))
        self.assertEqual(result.residual, Polynomial.constant(0))

    def test_equal_exact_constants_normalize_to_zero(self):
        equation = Equation(Rational(Fraction(2, 3)), Rational(Fraction(4, 6)))
        result = normalize_polynomial_equation(equation)
        self.assertEqual(result.residual, Polynomial.constant(0))

    def test_rule_metadata_is_explicit(self):
        result = normalize_polynomial_equation(Equation(self.x, self.y))
        self.assertEqual(result.rule_name, RULE_POLYNOMIAL_EQUATION_TO_ZERO)
        self.assertEqual(result.relation, "equivalent")
        self.assertEqual(result.side_conditions, ())

    def test_checker_accepts_valid_result(self):
        result = normalize_polynomial_equation(
            Equation(Add((self.x, Rational(3))), self.y)
        )
        self.assertTrue(verify_polynomial_equation_normal_form(result))

    def test_checker_rejects_tampered_residual(self):
        result = normalize_polynomial_equation(Equation(self.x, self.y))
        tampered = replace(result, residual=Polynomial.constant(0))
        self.assertFalse(verify_polynomial_equation_normal_form(tampered))

    def test_checker_rejects_wrong_result_type(self):
        self.assertFalse(verify_polynomial_equation_normal_form(object()))

    def test_non_equation_is_rejected(self):
        with self.assertRaises(TypeError):
            normalize_polynomial_equation(self.x)

    def test_unsupported_expression_is_rejected(self):
        equation = Equation(Power(self.x, Rational(-1)), Rational(1))
        with self.assertRaises(UnsupportedPolynomialExpression):
            normalize_polynomial_equation(equation)

    def test_polynomial_difference_is_exact(self):
        left = Polynomial.variable("x")
        right = Polynomial.constant(Fraction(1, 3))
        expected = Polynomial((
            ((("x", 1),), Fraction(1)),
            ((), Fraction(-1, 3)),
        ))
        self.assertEqual(polynomial_difference(left, right), expected)


class PolynomialEquationTransitionTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")
        self.y = Symbol("y")
        self.assumptions = Assumptions(positive=frozenset({"x"}))
        self.before = ProofState(
            (Equation(Add((self.x, Rational(1))), Multiply((Rational(2), self.x))),),
            self.assumptions,
        )

    def test_rule_builds_verified_transition_and_preserves_assumptions(self):
        step = apply_polynomial_equation_to_zero(self.before)
        self.assertEqual(step.rule_id, RULE_POLYNOMIAL_EQUATION_TO_ZERO)
        self.assertIs(step.semantics, RelationSemantics.EQUIVALENCE)
        self.assertEqual(step.side_conditions, ())
        self.assertEqual(step.after.assumptions, self.assumptions)
        self.assertTrue(verify_polynomial_equation_step(step))

    def test_transition_checker_rejects_tampered_output_state(self):
        step = apply_polynomial_equation_to_zero(self.before)
        tampered_after = ProofState(
            (Equation(self.x, Rational(0)),), self.assumptions
        )
        self.assertFalse(
            verify_polynomial_equation_step(replace(step, after=tampered_after))
        )

    def test_transition_checker_rejects_wrong_semantics(self):
        step = apply_polynomial_equation_to_zero(self.before)
        tampered = replace(step, semantics=RelationSemantics.FORWARD_IMPLICATION)
        self.assertFalse(verify_polynomial_equation_step(tampered))

    def test_transition_checker_rejects_unknown_rule(self):
        step = apply_polynomial_equation_to_zero(self.before)
        self.assertFalse(verify_polynomial_equation_step(replace(step, rule_id="other")))

    def test_transition_checker_rejects_added_side_condition(self):
        step = apply_polynomial_equation_to_zero(self.before)
        self.assertFalse(
            verify_polynomial_equation_step(
                replace(step, side_conditions=("x_nonzero",))
            )
        )

    def test_rule_rejects_states_with_multiple_relations(self):
        state = ProofState((
            Equation(self.x, Rational(1)),
            Equation(self.y, Rational(2)),
        ))
        with self.assertRaises(ValueError):
            apply_polynomial_equation_to_zero(state)

    def test_rule_rejects_unsupported_polynomial_fragment(self):
        state = ProofState((
            Equation(Power(self.x, Rational(-1)), Rational(1)),
        ))
        with self.assertRaises(UnsupportedPolynomialExpression):
            apply_polynomial_equation_to_zero(state)


if __name__ == "__main__":
    unittest.main()

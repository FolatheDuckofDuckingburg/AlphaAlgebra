import unittest
from dataclasses import replace
from fractions import Fraction

from alphaalgebra.core.ast import Add, Multiply, Power, Rational, Symbol
from alphaalgebra.core.polynomial import Polynomial, UnsupportedPolynomialExpression
from alphaalgebra.core.relations import Equation
from alphaalgebra.core.transformations import (
    RULE_POLYNOMIAL_EQUATION_TO_ZERO,
    normalize_polynomial_equation,
    polynomial_difference,
    verify_polynomial_equation_normal_form,
)


class PolynomialEquationNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")
        self.y = Symbol("y")

    def test_equation_is_moved_to_zero_exactly(self):
        equation = Equation(
            Add((self.x, Rational(1))),
            Multiply((Rational(2), self.x)),
        )
        result = normalize_polynomial_equation(equation)
        expected = Polynomial((
            ((), Fraction(1)),
            ((("x", 1),), Fraction(-1)),
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


if __name__ == "__main__":
    unittest.main()

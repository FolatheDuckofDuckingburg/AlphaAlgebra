import unittest
from fractions import Fraction

from alphaalgebra.core.ast import Add, Multiply, Power, Rational, Symbol
from alphaalgebra.core.polynomial import (
    Polynomial,
    UnsupportedPolynomialExpression,
    polynomial_from_expr,
)


class PolynomialTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")
        self.y = Symbol("y")

    def test_exact_constant_and_zero(self):
        self.assertEqual(
            Polynomial.constant(Fraction(2, 3)).terms,
            (((), Fraction(2, 3)),),
        )
        self.assertEqual(Polynomial.constant(0).terms, ())

    def test_like_terms_are_collected(self):
        expression = Add((self.x, self.x, Rational(Fraction(1, 2))))
        result = polynomial_from_expr(expression)
        self.assertEqual(
            result.terms,
            (((), Fraction(1, 2)), ((("x", 1),), Fraction(2))),
        )

    def test_expansion_and_collection(self):
        expression = Multiply((
            Add((self.x, Rational(1))),
            Add((self.x, Rational(-1))),
        ))
        result = polynomial_from_expr(expression)
        self.assertEqual(
            result.terms,
            (((), Fraction(-1)), ((("x", 2),), Fraction(1))),
        )

    def test_multivariate_monomials_are_canonical(self):
        expression = Multiply((self.y, self.x, self.y))
        result = polynomial_from_expr(expression)
        self.assertEqual(result.terms, (((("x", 1), ("y", 2)), Fraction(1)),))

    def test_power_zero_and_positive_integer(self):
        self.assertEqual(polynomial_from_expr(Power(self.x, Rational(0))),
                         Polynomial.constant(1))
        squared = polynomial_from_expr(Power(
            Add((self.x, Rational(1))), Rational(2)
        ))
        expected = Add((
            Power(self.x, Rational(2)),
            Multiply((Rational(2), self.x)),
            Rational(1),
        ))
        self.assertEqual(squared, polynomial_from_expr(expected))

    def test_negative_and_fractional_powers_are_rejected(self):
        for exponent in (Rational(-1), Rational(Fraction(1, 2))):
            with self.subTest(exponent=exponent):
                with self.assertRaises(UnsupportedPolynomialExpression):
                    polynomial_from_expr(Power(self.x, exponent))

    def test_symbolic_power_is_rejected(self):
        with self.assertRaises(UnsupportedPolynomialExpression):
            polynomial_from_expr(Power(self.x, self.y))

    def test_zero_coefficients_disappear(self):
        result = Polynomial((
            ((("x", 1),), Fraction(1)),
            ((("x", 1),), Fraction(-1)),
        ))
        self.assertEqual(result.terms, ())

    def test_invalid_polynomial_exponent_is_rejected(self):
        with self.assertRaises(ValueError):
            Polynomial.variable("x") ** -1


if __name__ == "__main__":
    unittest.main()

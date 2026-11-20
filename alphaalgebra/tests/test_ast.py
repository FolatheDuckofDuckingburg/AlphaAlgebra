import unittest
from fractions import Fraction

from alphaalgebra.core.ast import Add, Multiply, Power, Rational, Symbol


class RationalTests(unittest.TestCase):
    def test_exact_fraction_is_preserved(self):
        self.assertEqual(Rational(Fraction(2, 6)).value, Fraction(1, 3))

    def test_integer_is_converted_to_fraction(self):
        value = Rational(4)
        self.assertEqual(value.value, Fraction(4, 1))
        self.assertIsInstance(value.value, Fraction)

    def test_zero_denominator_is_rejected(self):
        with self.assertRaises(ZeroDivisionError):
            Rational.from_parts(1, 0)

    def test_float_is_rejected(self):
        with self.assertRaises(TypeError):
            Rational(0.1)


class ExpressionTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")
        self.one = Rational(1)

    def test_symbol_requires_name(self):
        with self.assertRaises(ValueError):
            Symbol(" ")

    def test_add_is_immutable_and_typed(self):
        expression = Add((self.x, self.one))
        self.assertEqual(expression.terms, (self.x, self.one))
        with self.assertRaises((AttributeError, TypeError)):
            expression.terms = (self.one, self.x)

    def test_add_requires_two_expression_terms(self):
        with self.assertRaises(ValueError):
            Add((self.x,))
        with self.assertRaises(TypeError):
            Add((self.x, "1"))

    def test_multiply_and_power(self):
        product = Multiply((self.x, self.one))
        self.assertEqual(product.factors[0], self.x)
        self.assertEqual(Power(self.x, Rational(2)).base, self.x)

    def test_power_children_must_be_nodes(self):
        with self.assertRaises(TypeError):
            Power(self.x, 2)


if __name__ == "__main__":
    unittest.main()

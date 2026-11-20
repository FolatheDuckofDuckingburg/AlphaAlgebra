import unittest

from alphaalgebra.core.ast import Rational, Symbol
from alphaalgebra.core.relations import (
    Equation, GreaterEqual, GreaterThan, LessEqual, LessThan,
)


class RelationTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")
        self.zero = Rational(0)

    def test_equation_preserves_both_sides(self):
        relation = Equation(self.x, self.zero)
        self.assertEqual(relation.left, self.x)
        self.assertEqual(relation.right, self.zero)

    def test_order_relations_are_distinct_types(self):
        self.assertIsInstance(LessThan(self.x, self.zero), LessThan)
        self.assertIsInstance(LessEqual(self.x, self.zero), LessEqual)
        self.assertIsInstance(GreaterThan(self.x, self.zero), GreaterThan)
        self.assertIsInstance(GreaterEqual(self.x, self.zero), GreaterEqual)

    def test_relation_requires_expression_nodes(self):
        with self.assertRaises(TypeError):
            Equation(self.x, 0)


if __name__ == "__main__":
    unittest.main()

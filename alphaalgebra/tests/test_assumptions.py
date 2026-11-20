import unittest

from alphaalgebra.core.assumptions import Assumptions


class AssumptionsTests(unittest.TestCase):
    def test_positive_implies_nonzero_in_representation(self):
        assumptions = Assumptions(positive=frozenset({"x"}))
        self.assertTrue(assumptions.is_positive("x"))
        self.assertTrue(assumptions.is_nonzero("x"))

    def test_nonzero_is_not_positive(self):
        assumptions = Assumptions(nonzero=frozenset({"x"}))
        self.assertTrue(assumptions.is_nonzero("x"))
        self.assertFalse(assumptions.is_positive("x"))

    def test_iterables_are_frozen(self):
        assumptions = Assumptions(positive={"x"})
        self.assertIsInstance(assumptions.positive, frozenset)
        self.assertTrue(assumptions.is_nonzero("x"))

    def test_empty_symbol_names_are_rejected(self):
        with self.assertRaises(ValueError):
            Assumptions(nonzero=frozenset({""}))


if __name__ == "__main__":
    unittest.main()

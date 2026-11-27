import unittest

from alphaalgebra.core.ast import Add, Multiply, Rational, Symbol
from alphaalgebra.core.assumptions import Assumptions
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation, LessThan
from alphaalgebra.search.state_keys import canonical_polynomial_state_key


class CanonicalPolynomialStateKeyTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")

    def test_expanded_and_unexpanded_equations_share_key(self):
        expanded = ProofState((Equation(
            Multiply((Add((self.x, Rational(1))), Add((self.x, Rational(-1))))),
            Rational(0),
        ),))
        collected = ProofState((Equation(
            Add((
                Multiply((Rational(1), self.x, self.x)),
                Rational(-1),
            )),
            Rational(0),
        ),))
        self.assertEqual(
            canonical_polynomial_state_key(expanded),
            canonical_polynomial_state_key(collected),
        )

    def test_assumptions_are_part_of_key(self):
        plain = ProofState((Equation(self.x, Rational(1)),))
        constrained = ProofState(
            (Equation(self.x, Rational(1)),),
            Assumptions(positive=frozenset({"x"})),
        )
        self.assertNotEqual(
            canonical_polynomial_state_key(plain),
            canonical_polynomial_state_key(constrained),
        )

    def test_non_equation_relations_use_structural_fallback(self):
        first = ProofState((LessThan(self.x, Rational(2)),))
        second = ProofState((LessThan(self.x, Rational(3)),))
        self.assertNotEqual(
            canonical_polynomial_state_key(first),
            canonical_polynomial_state_key(second),
        )

    def test_unsupported_equations_use_structural_fallback(self):
        first = ProofState((Equation(self.x, Symbol("y")),))
        second = ProofState((Equation(self.x, Symbol("z")),))
        self.assertNotEqual(
            canonical_polynomial_state_key(first),
            canonical_polynomial_state_key(second),
        )

    def test_key_is_hashable(self):
        state = ProofState((Equation(self.x, Rational(2)),))
        self.assertIsInstance(hash(canonical_polynomial_state_key(state)), int)


if __name__ == "__main__":
    unittest.main()

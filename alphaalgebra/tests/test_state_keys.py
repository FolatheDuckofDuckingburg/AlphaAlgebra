import unittest

from alphaalgebra.core.ast import Add, Multiply, Rational, Symbol
from alphaalgebra.core.assumptions import Assumptions
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation, LessThan
from alphaalgebra.search import canonical_polynomial_state_key


class CanonicalPolynomialStateKeyTests(unittest.TestCase):
    def test_expanded_and_factored_syntax_normalize_to_same_residual(self):
        x = Symbol("x")
        a = ProofState((Equation(Multiply((Add((x, Rational(1))), Add((x, Rational(-1))))), Rational(0)),))
        b = ProofState((Equation(Add((Multiply((x, x)), Rational(-1))), Rational(0)),))
        self.assertEqual(canonical_polynomial_state_key(a), canonical_polynomial_state_key(b))

    def test_assumptions_are_preserved_and_key_is_hashable(self):
        x = Symbol("x")
        plain = ProofState((Equation(x, Rational(1)),))
        positive = ProofState((Equation(x, Rational(1)),), Assumptions(positive=frozenset({"x"})))
        self.assertNotEqual(canonical_polynomial_state_key(plain), canonical_polynomial_state_key(positive))
        self.assertIsInstance(hash(canonical_polynomial_state_key(plain)), int)

    def test_unsupported_relations_fall_back_structurally(self):
        x = Symbol("x")
        self.assertNotEqual(
            canonical_polynomial_state_key(ProofState((LessThan(x, Rational(1)),))),
            canonical_polynomial_state_key(ProofState((LessThan(x, Rational(2)),))),
        )


if __name__ == "__main__":
    unittest.main()

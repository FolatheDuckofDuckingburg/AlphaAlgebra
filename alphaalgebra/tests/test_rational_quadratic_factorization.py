import unittest
from dataclasses import replace
from fractions import Fraction

from alphaalgebra.core.ast import Add, Multiply, Power, Rational, Symbol
from alphaalgebra.core.proof_state import ProofState, RelationSemantics
from alphaalgebra.core.relations import Equation
from alphaalgebra.core.transformations import (
    RULE_FACTOR_RATIONAL_QUADRATIC,
    apply_rational_quadratic_factorization,
    factor_rational_quadratic,
    verify_rational_quadratic_factorization_step,
)
from alphaalgebra.core.polynomial import Polynomial
from alphaalgebra.rules import RationalQuadraticFactorizationRule, default_rule_registry
from alphaalgebra.verification import verify_step
from alphaalgebra.search import SearchStatus, bounded_symbolic_search


class RationalQuadraticFactorizationTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")

    def state_for(self, a=1, b=-5, c=6):
        x2 = Power(self.x, Rational(2))
        terms = [Multiply((Rational(a), x2)), Multiply((Rational(b), self.x)), Rational(c)]
        return ProofState((Equation(Add(tuple(terms)), Rational(0)),))

    def test_factors_rational_roots_exactly(self):
        step = apply_rational_quadratic_factorization(self.state_for())
        expected = Multiply((
            Add((self.x, Rational(-3))),
            Add((self.x, Rational(-2))),
        ))
        self.assertEqual(step.after.relations[0], Equation(expected, Rational(0)))
        self.assertIs(step.semantics, RelationSemantics.EQUIVALENCE)
        self.assertEqual(step.rule_id, RULE_FACTOR_RATIONAL_QUADRATIC)
        self.assertTrue(verify_rational_quadratic_factorization_step(step))

    def test_preserves_non_unit_leading_coefficient(self):
        step = apply_rational_quadratic_factorization(self.state_for(2, -10, 12))
        expected = Multiply((
            Rational(2),
            Add((self.x, Rational(-3))),
            Add((self.x, Rational(-2))),
        ))
        self.assertEqual(step.after.relations[0], Equation(expected, Rational(0)))

    def test_repeated_rational_root(self):
        step = apply_rational_quadratic_factorization(self.state_for(1, -2, 1))
        expected = Multiply((
            Add((self.x, Rational(-1))),
            Add((self.x, Rational(-1))),
        ))
        self.assertEqual(step.after.relations[0], Equation(expected, Rational(0)))

    def test_accepts_fractional_rational_roots(self):
        state = self.state_for(2, -5, 2)
        step = apply_rational_quadratic_factorization(state)
        expected = Multiply((
            Rational(2),
            Add((self.x, Rational(-2))),
            Add((self.x, Rational(Fraction(-1, 2)))),
        ))
        self.assertEqual(step.after.relations[0], Equation(expected, Rational(0)))

    def test_checker_rejects_tampered_output_and_semantics(self):
        step = apply_rational_quadratic_factorization(self.state_for())
        wrong = replace(step, after=self.state_for())
        wrong_semantics = replace(step, semantics=RelationSemantics.FORWARD_IMPLICATION)
        self.assertFalse(verify_rational_quadratic_factorization_step(wrong))
        self.assertFalse(verify_rational_quadratic_factorization_step(wrong_semantics))

    def test_rejects_irrational_or_nonreal_roots(self):
        for coefficients in ((1, -2, -1), (1, 0, 1)):
            with self.subTest(coefficients=coefficients):
                with self.assertRaises(ValueError):
                    apply_rational_quadratic_factorization(
                        self.state_for(*coefficients)
                    )

    def test_rejects_multivariate_quadratic(self):
        y = Symbol("y")
        state = ProofState((Equation(
            Add((
                Power(self.x, Rational(2)),
                Multiply((self.x, y)),
                Rational(1),
            )),
            Rational(0),
        ),))
        with self.assertRaises(ValueError):
            apply_rational_quadratic_factorization(state)

    def test_rule_is_independently_registered(self):
        registry = default_rule_registry()
        rule = registry.get(RULE_FACTOR_RATIONAL_QUADRATIC)
        self.assertIsInstance(rule, RationalQuadraticFactorizationRule)
        proposal = rule.apply(self.state_for())
        self.assertTrue(verify_step(proposal, registry).valid)


    def test_bounded_search_can_reach_factored_form(self):
        result = bounded_symbolic_search(
            self.state_for(),
            lambda state: (
                isinstance(state.relations[0], Equation)
                and isinstance(state.relations[0].left, Multiply)
            ),
            default_rule_registry(),
            max_depth=1,
            max_expanded_nodes=10,
        )
        self.assertEqual(result.status, SearchStatus.SOLVED)
        self.assertEqual(len(result.proof), 1)
        self.assertEqual(
            result.proof[0].rule_id,
            RULE_FACTOR_RATIONAL_QUADRATIC,
        )

    def test_rational_square_root_requires_exact_square(self):
        self.assertIsNone(factor_rational_quadratic(Polynomial((
            (((("x", 2),)), Fraction(1)),
            ((("x", 1),), Fraction(-2)),
            ((), Fraction(-1)),
        ))))


if __name__ == "__main__":
    unittest.main()

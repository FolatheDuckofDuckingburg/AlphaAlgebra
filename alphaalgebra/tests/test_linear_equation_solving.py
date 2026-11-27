import unittest
from dataclasses import replace
from fractions import Fraction

from alphaalgebra.core.ast import Add, Multiply, Power, Rational, Symbol
from alphaalgebra.core.proof_state import ProofState, RelationSemantics
from alphaalgebra.core.relations import Equation
from alphaalgebra.core.transformations import (
    RULE_SOLVE_LINEAR_EQUATION,
    apply_linear_equation_solution,
    verify_linear_equation_solution_step,
)
from alphaalgebra.rules import LinearEquationSolvingRule, default_rule_registry
from alphaalgebra.search import SearchStatus, bounded_symbolic_search
from alphaalgebra.verification import verify_step


class LinearEquationSolvingTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")

    def state(self, left, right=Rational(0)):
        return ProofState((Equation(left, right),))

    def test_solves_integer_coefficient_equation(self):
        state = self.state(Add((Multiply((Rational(3), self.x)), Rational(2))))
        step = apply_linear_equation_solution(state)
        self.assertEqual(
            step.after.relations[0],
            Equation(self.x, Rational(Fraction(-2, 3))),
        )
        self.assertIs(step.semantics, RelationSemantics.EQUIVALENCE)
        self.assertTrue(verify_linear_equation_solution_step(step))

    def test_solves_equation_with_variable_on_both_sides(self):
        state = self.state(
            Add((Multiply((Rational(5), self.x)), Rational(1))),
            Add((Multiply((Rational(2), self.x)), Rational(7))),
        )
        step = apply_linear_equation_solution(state)
        self.assertEqual(
            step.after.relations[0],
            Equation(self.x, Rational(2)),
        )

    def test_preserves_assumptions(self):
        from alphaalgebra.core.assumptions import Assumptions
        assumptions = Assumptions()
        state = ProofState((Equation(
            Add((Multiply((Rational(4), self.x)), Rational(-8))),
            Rational(0),
        ),), assumptions)
        self.assertEqual(
            apply_linear_equation_solution(state).after.assumptions,
            assumptions,
        )

    def test_rejects_constant_zero_coefficient_and_nonlinear_equations(self):
        cases = (
            self.state(Rational(5)),
            self.state(Rational(0)),
            self.state(Add((Power(self.x, Rational(2)), Rational(1)))),
        )
        for state in cases:
            with self.subTest(state=state):
                with self.assertRaises(ValueError):
                    apply_linear_equation_solution(state)

    def test_rejects_multivariate_linear_equation(self):
        y = Symbol("y")
        state = self.state(Add((self.x, y, Rational(1))))
        with self.assertRaises(ValueError):
            apply_linear_equation_solution(state)

    def test_checker_rejects_tampered_solution_and_semantics(self):
        step = apply_linear_equation_solution(
            self.state(Add((Multiply((Rational(2), self.x)), Rational(6))))
        )
        tampered = replace(
            step,
            after=ProofState((Equation(self.x, Rational(99)),)),
        )
        wrong_semantics = replace(
            step,
            semantics=RelationSemantics.FORWARD_IMPLICATION,
        )
        self.assertFalse(verify_linear_equation_solution_step(tampered))
        self.assertFalse(verify_linear_equation_solution_step(wrong_semantics))

    def test_rule_is_registered_and_verifier_accepts_transition(self):
        state = self.state(Add((Multiply((Rational(7), self.x)), Rational(-14))))
        registry = default_rule_registry()
        rule = registry.get(RULE_SOLVE_LINEAR_EQUATION)
        self.assertIsInstance(rule, LinearEquationSolvingRule)
        self.assertTrue(verify_step(rule.apply(state), registry).valid)

    def test_search_finds_linear_solution(self):
        state = self.state(Add((Multiply((Rational(4), self.x)), Rational(-12))))
        result = bounded_symbolic_search(
            state,
            lambda candidate: candidate.relations == (Equation(self.x, Rational(3)),),
            default_rule_registry(),
            max_depth=2,
            max_expanded_nodes=20,
        )
        self.assertEqual(result.status, SearchStatus.SOLVED)
        self.assertEqual(result.proof[-1].rule_id, RULE_SOLVE_LINEAR_EQUATION)


if __name__ == "__main__":
    unittest.main()

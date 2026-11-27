import unittest

from alphaalgebra.core.ast import Add, Multiply, Rational, Symbol
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation
from alphaalgebra.problem import EquationSolutionGoal
from alphaalgebra.rules import default_rule_registry
from alphaalgebra.search import SearchStatus, bounded_symbolic_search


class EquationSolutionGoalTests(unittest.TestCase):
    def test_exact_goal_and_search_integration(self):
        x = Symbol("x")
        state = ProofState((Equation(Add((Multiply((Rational(2), x)), Rational(-6))), Rational(0)),))
        result = bounded_symbolic_search(
            state, EquationSolutionGoal("x", Rational(3)),
            default_rule_registry(), max_depth=2, max_expanded_nodes=20,
        )
        self.assertEqual(result.status, SearchStatus.SOLVED)
        self.assertEqual(result.proof[-1].rule_id, "solve_linear_equation")

    def test_wrong_value_variable_and_state_are_rejected(self):
        x = Symbol("x")
        state = ProofState((Equation(x, Rational(3)),))
        self.assertTrue(EquationSolutionGoal("x", Rational(3)).is_satisfied(state))
        self.assertFalse(EquationSolutionGoal("y", Rational(3)).is_satisfied(state))
        self.assertFalse(EquationSolutionGoal("x", Rational(4)).is_satisfied(state))
        self.assertFalse(EquationSolutionGoal("x", Rational(3)).is_satisfied(object()))

    def test_goal_validates_fields(self):
        with self.assertRaises(ValueError):
            EquationSolutionGoal(" ", Rational(1))
        with self.assertRaises(TypeError):
            EquationSolutionGoal("x", Symbol("y"))


if __name__ == "__main__":
    unittest.main()

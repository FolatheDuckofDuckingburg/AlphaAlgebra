import unittest

from alphaalgebra.core.ast import Add, Multiply, Rational, Symbol
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation
from alphaalgebra.problem import EquationSolutionGoal
from alphaalgebra.rules import default_rule_registry
from alphaalgebra.search import SearchStatus, bounded_symbolic_search


class EquationSolutionGoalTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")

    def test_matches_exact_solution_state(self):
        goal = EquationSolutionGoal("x", Rational(3))
        state = ProofState((Equation(self.x, Rational(3)),))
        self.assertTrue(goal.is_satisfied(state))

    def test_rejects_wrong_variable_or_value(self):
        state = ProofState((Equation(self.x, Rational(3)),))
        self.assertFalse(EquationSolutionGoal("y", Rational(3)).is_satisfied(state))
        self.assertFalse(EquationSolutionGoal("x", Rational(4)).is_satisfied(state))

    def test_rejects_non_solution_and_multi_relation_states(self):
        goal = EquationSolutionGoal("x", Rational(3))
        self.assertFalse(goal.is_satisfied(ProofState((
            Equation(Add((self.x, Rational(1))), Rational(0)),
        ))))
        self.assertFalse(goal.is_satisfied(ProofState((
            Equation(self.x, Rational(3)),
            Equation(Symbol("y"), Rational(2)),
        ))))

    def test_validates_goal_fields(self):
        with self.assertRaises(ValueError):
            EquationSolutionGoal(" ", Rational(1))
        with self.assertRaises(TypeError):
            EquationSolutionGoal("x", Symbol("y"))

    def test_search_accepts_typed_goal(self):
        state = ProofState((Equation(
            Add((Multiply((Rational(2), self.x)), Rational(-6))),
            Rational(0),
        ),))
        result = bounded_symbolic_search(
            state,
            EquationSolutionGoal("x", Rational(3)),
            default_rule_registry(),
            max_depth=2,
            max_expanded_nodes=20,
        )
        self.assertEqual(result.status, SearchStatus.SOLVED)
        self.assertEqual(result.proof[-1].rule_id, "solve_linear_equation")


if __name__ == "__main__":
    unittest.main()

import unittest

from alphaalgebra.core.ast import Rational, Symbol
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation
from alphaalgebra.rules.registry import default_rule_registry
from alphaalgebra.search import SearchStatus, bounded_symbolic_search


class BoundedSymbolicSearchTests(unittest.TestCase):
    def setUp(self):
        self.initial = ProofState((Equation(Symbol("x"), Rational(2)),))
        self.registry = default_rule_registry()

    def test_finds_goal_with_verified_proof_path(self):
        result = bounded_symbolic_search(
            self.initial,
            lambda state: state != self.initial
            and len(state.relations) == 1
            and isinstance(state.relations[0], Equation)
            and state.relations[0].right == Rational(0),
            self.registry,
            max_depth=2,
            max_expanded_nodes=10,
        )
        self.assertEqual(result.status, SearchStatus.SOLVED)
        self.assertTrue(result.solved)
        self.assertEqual(len(result.proof), 1)
        self.assertEqual(result.proof[0].before, self.initial)
        self.assertEqual(result.proof[0].after.relations[0].right, Rational(0))
        self.assertEqual(result.expanded_nodes, 1)

    def test_initial_state_can_already_satisfy_goal(self):
        result = bounded_symbolic_search(
            self.initial, lambda state: state == self.initial, self.registry
        )
        self.assertEqual(result.status, SearchStatus.SOLVED)
        self.assertEqual(result.proof, ())
        self.assertEqual(result.expanded_nodes, 0)

    def test_depth_limit_is_reported_separately(self):
        result = bounded_symbolic_search(
            self.initial, lambda state: False, self.registry, max_depth=0
        )
        self.assertEqual(result.status, SearchStatus.DEPTH_LIMIT_REACHED)
        self.assertEqual(result.expanded_nodes, 0)

    def test_node_budget_is_enforced(self):
        result = bounded_symbolic_search(
            self.initial, lambda state: False, self.registry, max_expanded_nodes=0
        )
        self.assertEqual(result.status, SearchStatus.NODE_BUDGET_EXHAUSTED)
        self.assertEqual(result.expanded_nodes, 0)

    def test_frontier_exhaustion_is_reported(self):
        result = bounded_symbolic_search(
            self.initial, lambda state: False, self.registry, max_depth=4
        )
        self.assertEqual(result.status, SearchStatus.FRONTIER_EXHAUSTED)
        self.assertEqual(result.expanded_nodes, 2)
        self.assertEqual(result.discovered_states, 2)

    def test_negative_budgets_are_rejected(self):
        with self.assertRaises(ValueError):
            bounded_symbolic_search(
                self.initial, lambda state: False, self.registry, max_depth=-1
            )


    def test_wall_clock_budget_reports_time_limit(self):
        result = bounded_symbolic_search(
            self.initial,
            lambda state: False,
            self.registry,
            max_seconds=0,
        )
        self.assertEqual(result.status, SearchStatus.TIME_LIMIT_REACHED)
        self.assertEqual(result.expanded_nodes, 0)

    def test_initial_goal_is_checked_before_zero_time_budget(self):
        result = bounded_symbolic_search(
            self.initial,
            lambda state: state == self.initial,
            self.registry,
            max_seconds=0,
        )
        self.assertEqual(result.status, SearchStatus.SOLVED)

    def test_invalid_wall_clock_budgets_are_rejected(self):
        for value in (-1, float("inf"), float("nan"), True, "1"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    bounded_symbolic_search(
                        self.initial,
                        lambda state: False,
                        self.registry,
                        max_seconds=value,
                    )

    def test_non_callable_goal_is_rejected(self):
        with self.assertRaises(TypeError):
            bounded_symbolic_search(self.initial, None, self.registry)


if __name__ == "__main__":
    unittest.main()

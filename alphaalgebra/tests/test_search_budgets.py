import unittest

from alphaalgebra.core.ast import Rational, Symbol
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation
from alphaalgebra.rules.registry import default_rule_registry
from alphaalgebra.search import SearchStatus, bounded_symbolic_search


class SearchBudgetTests(unittest.TestCase):
    def setUp(self):
        self.state = ProofState((Equation(Symbol("x"), Rational(2)),))
        self.registry = default_rule_registry()

    def test_zero_time_budget_reports_time_limit(self):
        result = bounded_symbolic_search(self.state, lambda _: False, self.registry, max_seconds=0)
        self.assertEqual(result.status, SearchStatus.TIME_LIMIT_REACHED)
        self.assertEqual(result.expanded_nodes, 0)

    def test_initial_goal_precedes_zero_time_budget(self):
        result = bounded_symbolic_search(self.state, lambda s: s == self.state, self.registry, max_seconds=0)
        self.assertEqual(result.status, SearchStatus.SOLVED)

    def test_invalid_time_budgets_rejected(self):
        for value in (-1, float("inf"), float("nan"), True, "1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bounded_symbolic_search(self.state, lambda _: False, self.registry, max_seconds=value)


if __name__ == "__main__":
    unittest.main()

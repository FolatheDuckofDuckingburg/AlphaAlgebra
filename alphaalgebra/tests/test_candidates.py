import unittest
from dataclasses import replace

from alphaalgebra.core.ast import Rational, Symbol
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation
from alphaalgebra.core.transformations import verify_polynomial_equation_step
from alphaalgebra.rules.polynomial import PolynomialEquationToZeroRule
from alphaalgebra.rules.registry import RuleRegistry, default_rule_registry
from alphaalgebra.search.candidates import generate_candidates


class CandidateGenerationTests(unittest.TestCase):
    def setUp(self):
        self.state = ProofState((Equation(Symbol("x"), Rational(2)),))
        self.registry = default_rule_registry()

    def test_only_verified_candidates_are_returned(self):
        generated = generate_candidates(self.state, self.registry)
        self.assertEqual(len(generated.candidates), 1)
        self.assertEqual(generated.candidates[0].before, self.state)
        self.assertEqual(generated.rejected, ())

    def test_non_applicable_state_has_no_candidates(self):
        state = ProofState((Equation(Symbol("x"), Symbol("y")), Equation(Symbol("z"), Rational(0))))
        generated = generate_candidates(state, self.registry)
        self.assertEqual(generated.candidates, ())
        self.assertEqual(generated.rejected, ())

    def test_checker_rejection_keeps_proposal_out_of_frontier(self):
        registry = RuleRegistry()
        registry.register(PolynomialEquationToZeroRule(), lambda step: False)
        generated = generate_candidates(self.state, registry)
        self.assertEqual(generated.candidates, ())
        self.assertEqual(len(generated.rejected), 1)
        self.assertEqual(generated.rejected[0].reason, "checker_rejected_transition")

    def test_rule_proposal_must_start_at_requested_state(self):
        registry = RuleRegistry()

        class WrongSourceRule(PolynomialEquationToZeroRule):
            rule_id = "wrong_source_test_rule"

            def apply(self, state):
                step = super().apply(state)
                other = ProofState((Equation(Symbol("y"), Rational(9)),))
                return replace(step, rule_id=self.rule_id, before=other)

        registry.register(WrongSourceRule(), lambda step: True)
        generated = generate_candidates(self.state, registry)
        self.assertEqual(generated.candidates, ())
        self.assertEqual(generated.rejected[0].reason, "source_state_mismatch")

    def test_rule_application_failure_is_recorded(self):
        registry = RuleRegistry()

        class BrokenRule(PolynomialEquationToZeroRule):
            rule_id = "broken_test_rule"

            def apply(self, state):
                raise RuntimeError("synthetic rule failure")

        registry.register(BrokenRule(), verify_polynomial_equation_step)
        generated = generate_candidates(self.state, registry)
        self.assertEqual(generated.candidates, ())
        self.assertEqual(generated.rejected[0].reason, "rule_application_error")


if __name__ == "__main__":
    unittest.main()

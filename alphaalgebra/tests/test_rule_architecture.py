import unittest
from dataclasses import replace

from alphaalgebra.core.ast import Rational, Symbol
from alphaalgebra.core.proof_state import ProofState
from alphaalgebra.core.relations import Equation
from alphaalgebra.rules import PolynomialEquationToZeroRule, RuleRegistry, default_rule_registry
from alphaalgebra.verification import verify_step


class RuleArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")
        self.state = ProofState((Equation(self.x, Rational(2)),))
        self.registry = default_rule_registry()

    def test_default_registry_exposes_only_supported_rule(self):
        self.assertEqual(self.registry.rule_ids, ("polynomial_equation_to_zero",))

    def test_rule_proposes_transition_and_verifier_accepts_it(self):
        rule = self.registry.get("polynomial_equation_to_zero")
        self.assertIsInstance(rule, PolynomialEquationToZeroRule)
        self.assertTrue(rule.is_applicable(self.state))
        step = rule.apply(self.state)
        result = verify_step(step, self.registry)
        self.assertTrue(result.valid)
        self.assertEqual(result.reason, "verified_by_registered_checker")

    def test_non_applicable_state_is_not_proposed(self):
        rule = self.registry.get("polynomial_equation_to_zero")
        state = ProofState((Equation(Symbol("x"), Symbol("y")), Equation(self.x, Rational(1))))
        self.assertFalse(rule.is_applicable(state))

    def test_tampered_step_fails_closed(self):
        rule = self.registry.get("polynomial_equation_to_zero")
        step = rule.apply(self.state)
        tampered = replace(step, after=self.state)
        self.assertFalse(verify_step(tampered, self.registry).valid)

    def test_unknown_rule_is_rejected(self):
        rule = self.registry.get("polynomial_equation_to_zero")
        step = replace(rule.apply(self.state), rule_id="unregistered")
        result = verify_step(step, self.registry)
        self.assertFalse(result.valid)
        self.assertEqual(result.reason, "unregistered_rule")

    def test_duplicate_rule_registration_is_rejected(self):
        rule = PolynomialEquationToZeroRule()
        from alphaalgebra.core.transformations import verify_polynomial_equation_step
        registry = RuleRegistry()
        registry.register(rule, verify_polynomial_equation_step)
        with self.assertRaises(ValueError):
            registry.register(rule, verify_polynomial_equation_step)


if __name__ == "__main__":
    unittest.main()

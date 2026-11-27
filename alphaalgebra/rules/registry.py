"""Deterministic registry separating rule proposals from verification."""

from dataclasses import dataclass, field
from typing import Callable

from alphaalgebra.core.proof_state import TransformationStep
from .base import TransformationRule

StepChecker = Callable[[TransformationStep], bool]


@dataclass
class RuleRegistry:
    """Registry of rule implementations and independently supplied checkers."""

    _rules: dict[str, TransformationRule] = field(default_factory=dict)
    _checkers: dict[str, StepChecker] = field(default_factory=dict)

    def register(self, rule: TransformationRule, checker: StepChecker) -> None:
        if not isinstance(rule.rule_id, str) or not rule.rule_id.strip():
            raise ValueError("rule_id must be a non-empty string")
        if not isinstance(rule.version, str) or not rule.version.strip():
            raise ValueError("rule version must be a non-empty string")
        if rule.rule_id in self._rules:
            raise ValueError(f"rule already registered: {rule.rule_id}")
        if not callable(checker):
            raise TypeError("checker must be callable")
        self._rules[rule.rule_id] = rule
        self._checkers[rule.rule_id] = checker

    def get(self, rule_id: str) -> TransformationRule:
        try:
            return self._rules[rule_id]
        except KeyError as exc:
            raise KeyError(f"unknown transformation rule: {rule_id}") from exc

    def checker_for(self, rule_id: str) -> StepChecker:
        try:
            return self._checkers[rule_id]
        except KeyError as exc:
            raise KeyError(f"no verifier registered for rule: {rule_id}") from exc

    def applicable_rules(self, state) -> tuple[TransformationRule, ...]:
        return tuple(
            rule for rule in self._rules.values() if rule.is_applicable(state)
        )

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._rules))


def default_rule_registry() -> RuleRegistry:
    """Build a fresh registry with only independently checked initial rules."""
    from alphaalgebra.core.transformations import (
        verify_polynomial_equation_step,
        verify_rational_quadratic_factorization_step,\n        verify_linear_equation_solution_step,
    )
    from .polynomial import PolynomialEquationToZeroRule, RationalQuadraticFactorizationRule, LinearEquationSolvingRule

    registry = RuleRegistry()
    registry.register(PolynomialEquationToZeroRule(), verify_polynomial_equation_step)
    registry.register(
        RationalQuadraticFactorizationRule(),
        verify_rational_quadratic_factorization_step,
    )
    return registry

"""Independent dispatch for checking proposed transformation transitions."""

from dataclasses import dataclass

from alphaalgebra.core.proof_state import TransformationStep
from alphaalgebra.rules.registry import RuleRegistry


@dataclass(frozen=True, slots=True)
class VerificationResult:
    valid: bool
    rule_id: str
    reason: str


def verify_step(step: TransformationStep, registry: RuleRegistry) -> VerificationResult:
    """Verify a proposed step using its registered checker, not its producer.

    Unknown rules, malformed steps, and checker exceptions fail closed. This
    dispatcher does not prove arbitrary equivalence or logical entailment.
    """
    if not isinstance(step, TransformationStep):
        return VerificationResult(False, "", "not_a_transformation_step")
    if not isinstance(registry, RuleRegistry):
        raise TypeError("registry must be a RuleRegistry")
    try:
        checker = registry.checker_for(step.rule_id)
    except KeyError:
        return VerificationResult(False, step.rule_id, "unregistered_rule")
    try:
        accepted = checker(step)
    except Exception:
        return VerificationResult(False, step.rule_id, "checker_error")
    if accepted is not True:
        return VerificationResult(False, step.rule_id, "checker_rejected_transition")
    return VerificationResult(True, step.rule_id, "verified_by_registered_checker")

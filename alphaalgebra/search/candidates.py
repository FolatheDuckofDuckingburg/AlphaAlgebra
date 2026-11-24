"""Generate only independently verified symbolic transformation candidates.

Rules propose transitions. This module checks that each proposal starts at the
requested state and delegates mathematical checking to the registry's separate
checker. Failed proposals are recorded rather than entering the search frontier.
"""

from dataclasses import dataclass

from alphaalgebra.core.proof_state import ProofState, TransformationStep
from alphaalgebra.rules.registry import RuleRegistry
from alphaalgebra.verification.verifier import verify_step


@dataclass(frozen=True, slots=True)
class CandidateRejection:
    """A rule proposal excluded from the frontier, with a stable reason code."""

    rule_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class CandidateGeneration:
    """Verified transitions and rejected proposals from one source state."""

    candidates: tuple[TransformationStep, ...]
    rejected: tuple[CandidateRejection, ...]


def generate_candidates(state: ProofState, registry: RuleRegistry) -> CandidateGeneration:
    """Enumerate applicable rules deterministically and verify every proposal.

    Only transitions whose before state exactly matches state and whose
    registered independent checker accepts them are returned as candidates.
    Rule failures are isolated and represented by reason codes. This function
    does not claim that the candidate set is complete for any algebra domain.
    """
    if not isinstance(state, ProofState):
        raise TypeError("state must be a ProofState")
    if not isinstance(registry, RuleRegistry):
        raise TypeError("registry must be a RuleRegistry")

    candidates: list[TransformationStep] = []
    rejected: list[CandidateRejection] = []
    rules = sorted(registry.applicable_rules(state), key=lambda rule: (rule.rule_id, rule.version))

    for rule in rules:
        try:
            proposal = rule.apply(state)
        except Exception:
            rejected.append(CandidateRejection(rule.rule_id, "rule_application_error"))
            continue

        if not isinstance(proposal, TransformationStep):
            rejected.append(CandidateRejection(rule.rule_id, "not_a_transformation_step"))
            continue
        if proposal.before != state:
            rejected.append(CandidateRejection(rule.rule_id, "source_state_mismatch"))
            continue

        result = verify_step(proposal, registry)
        if not result.valid:
            rejected.append(CandidateRejection(rule.rule_id, result.reason))
            continue
        candidates.append(proposal)

    return CandidateGeneration(tuple(candidates), tuple(rejected))

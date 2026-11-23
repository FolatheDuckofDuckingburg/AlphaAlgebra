import unittest
from dataclasses import FrozenInstanceError

from alphaalgebra.core.ast import Rational, Symbol
from alphaalgebra.core.assumptions import Assumptions
from alphaalgebra.core.proof_state import (
    ProofState, RelationSemantics, TransformationStep,
)
from alphaalgebra.core.relations import Equation


class ProofStateTests(unittest.TestCase):
    def setUp(self):
        self.x = Symbol("x")
        self.source = ProofState(
            (Equation(self.x, Rational(1)),),
            Assumptions(nonzero=frozenset({"x"})),
        )
        self.target = ProofState((Equation(self.x, Rational(1)),), self.source.assumptions)

    def test_state_freezes_relation_iterables(self):
        state = ProofState([Equation(self.x, Rational(1))])
        self.assertIsInstance(state.relations, tuple)

    def test_state_rejects_non_relations(self):
        with self.assertRaises(TypeError):
            ProofState((self.x,))

    def test_state_requires_explicit_assumptions_type(self):
        with self.assertRaises(TypeError):
            ProofState((), assumptions=None)

    def test_step_records_equivalence_and_conditions(self):
        step = TransformationStep(
            "example_rule", self.source, self.target,
            RelationSemantics.EQUIVALENCE, ("x_is_nonzero",),
        )
        self.assertEqual(step.rule_id, "example_rule")
        self.assertEqual(step.semantics, RelationSemantics.EQUIVALENCE)
        self.assertEqual(step.side_conditions, ("x_is_nonzero",))

    def test_implication_directions_are_distinct(self):
        self.assertNotEqual(
            RelationSemantics.FORWARD_IMPLICATION,
            RelationSemantics.REVERSE_IMPLICATION,
        )

    def test_step_rejects_empty_rule_identifier(self):
        with self.assertRaises(ValueError):
            TransformationStep("", self.source, self.target, RelationSemantics.EQUIVALENCE)

    def test_step_rejects_untyped_semantics(self):
        with self.assertRaises(TypeError):
            TransformationStep("rule", self.source, self.target, "equivalent")

    def test_step_is_immutable(self):
        step = TransformationStep("rule", self.source, self.target, RelationSemantics.EQUIVALENCE)
        with self.assertRaises(FrozenInstanceError):
            step.rule_id = "changed"


if __name__ == "__main__":
    unittest.main()

import unittest

from src.evidence_state.schema import (
    ALLOWED_EVIDENCE_STATES,
    ALLOWED_ROUTER_ACTIONS,
    DEFAULT_ROUTER_ACTION_BY_STATE,
    EvidenceItem,
    EvidencePair,
    EvidenceStateValidationError,
)


class EvidenceStateSchemaTests(unittest.TestCase):
    def test_allows_only_declared_evidence_states(self):
        self.assertEqual(
            ALLOWED_EVIDENCE_STATES, ("sufficient", "insufficient", "conflict")
        )

        item = _item(evidence_state="sufficient")
        self.assertEqual(item.evidence_state, "sufficient")

        with self.assertRaisesRegex(
            EvidenceStateValidationError,
            "evidence_state must be one of conflict, insufficient, sufficient",
        ):
            _item(evidence_state="ambiguous")

    def test_allows_only_declared_router_actions(self):
        self.assertEqual(ALLOWED_ROUTER_ACTIONS, ("proceed", "retrieve", "abstain"))

        item = _item(expected_action="proceed")
        self.assertEqual(item.expected_action, "proceed")

        for rejected_action in ("clarify", "answer"):
            with self.subTest(rejected_action=rejected_action):
                with self.assertRaisesRegex(
                    EvidenceStateValidationError,
                    "expected_action must be one of abstain, proceed, retrieve",
                ):
                    _item(expected_action=rejected_action)

    def test_requires_default_action_for_each_evidence_state(self):
        expected_actions = {
            "sufficient": "proceed",
            "insufficient": "retrieve",
            "conflict": "abstain",
        }
        self.assertEqual(DEFAULT_ROUTER_ACTION_BY_STATE, expected_actions)

        for evidence_state, expected_action in expected_actions.items():
            with self.subTest(evidence_state=evidence_state):
                item = _item(
                    evidence_state=evidence_state,
                    expected_action=expected_action,
                )
                self.assertEqual(item.expected_action, expected_action)

                incompatible_action = {
                    "proceed": "retrieve",
                    "retrieve": "abstain",
                    "abstain": "proceed",
                }[expected_action]
                with self.assertRaisesRegex(
                    EvidenceStateValidationError,
                    f"expected_action for {evidence_state} evidence_state must be {expected_action}",
                ):
                    _item(
                        evidence_state=evidence_state,
                        expected_action=incompatible_action,
                    )

    def test_pair_preserves_question_and_differs_only_in_evidence_state(self):
        sufficient = _item(
            item_id="pair-1:sufficient",
            evidence_state="sufficient",
            expected_action="proceed",
            evidence=["The report states that Ada won the award."],
        )
        conflict = _item(
            item_id="pair-1:conflict",
            evidence_state="conflict",
            expected_action="abstain",
            evidence=[
                "The report states that Ada won the award.",
                "A correction states that Ben won the award.",
            ],
            intervention={
                "kind": "add_conflicting_sentence",
                "evidence_index": 1,
                "field": "evidence",
            },
        )

        pair = EvidencePair(pair_id="pair-1", first=sufficient, second=conflict)

        self.assertEqual(pair.question, "Who won the award?")
        self.assertEqual(pair.evidence_states, ("sufficient", "conflict"))

    def test_pair_rejects_changed_question_or_non_evidence_state_changes(self):
        sufficient = _item(
            item_id="pair-2:sufficient",
            pair_id="pair-2",
            evidence_state="sufficient",
        )
        changed_question = _item(
            item_id="pair-2:insufficient",
            pair_id="pair-2",
            question="Who lost the award?",
            evidence_state="insufficient",
            expected_action="retrieve",
            intervention={
                "kind": "remove_required_premise",
                "evidence_index": 0,
                "field": "evidence",
            },
        )
        changed_answer = _item(
            item_id="pair-2:conflict",
            pair_id="pair-2",
            evidence_state="conflict",
            answer="Ben",
            expected_action="abstain",
            intervention={
                "kind": "add_conflicting_sentence",
                "evidence_index": 1,
                "field": "evidence",
            },
        )

        with self.assertRaisesRegex(EvidenceStateValidationError, "same question"):
            EvidencePair(pair_id="pair-2", first=sufficient, second=changed_question)

        with self.assertRaisesRegex(
            EvidenceStateValidationError, "only evidence_state may differ"
        ):
            EvidencePair(pair_id="pair-2", first=sufficient, second=changed_answer)

    def test_intervention_fields_are_explicitly_validated(self):
        valid = _item(
            evidence_state="insufficient",
            expected_action="retrieve",
            intervention={
                "kind": "remove_required_premise",
                "evidence_index": 0,
                "field": "evidence",
            },
        )
        self.assertEqual(valid.intervention["kind"], "remove_required_premise")

        with self.assertRaisesRegex(
            EvidenceStateValidationError,
            "intervention.kind must be one of add_conflicting_sentence, remove_conflicting_sentence, remove_required_premise, restore_required_premise",
        ):
            _item(intervention={"kind": "rewrite_question", "field": "question"})

        with self.assertRaisesRegex(
            EvidenceStateValidationError, "intervention.field must be evidence"
        ):
            _item(intervention={"kind": "restore_required_premise", "field": "answer"})


def _item(
    *,
    item_id="pair-1:sufficient",
    pair_id="pair-1",
    question="Who won the award?",
    evidence_state="sufficient",
    evidence=None,
    answer="Ada",
    expected_action=None,
    intervention=None,
):
    if evidence is None:
        evidence = ["The report states that Ada won the award."]
    if intervention is None:
        intervention = {
            "kind": "restore_required_premise",
            "evidence_index": 0,
            "field": "evidence",
        }
    if expected_action is None:
        expected_action = {
            "sufficient": "proceed",
            "insufficient": "retrieve",
            "conflict": "abstain",
        }.get(evidence_state, "proceed")
    return EvidenceItem(
        item_id=item_id,
        pair_id=pair_id,
        question=question,
        evidence=tuple(evidence),
        answer=answer,
        evidence_state=evidence_state,
        expected_action=expected_action,
        intervention=intervention,
        source_ids=("source-1",),
    )


if __name__ == "__main__":
    unittest.main()

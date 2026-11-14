"""Feedback must be explicit, optional and attached to the delivered version."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("feedback_checker", ROOT / "tools/check_blueprint.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.pending = json.loads((ROOT / "examples/feedback/pending.json").read_text(encoding="utf-8"))

    def answered(self, choice="accepted"):
        doc = copy.deepcopy(self.pending)
        doc["feedback"] = {"status": "responded", "response": {
            "choice": choice, "source": "user", "received_at": "2026-01-01T12:00:00+00:00",
            "delivery_sha256": doc["delivery_sha256"], "comment": "Fictional test response only."}}
        return doc

    def test_no_response_remains_pending(self):
        self.assertEqual(checker.validate_feedback_record(self.pending), [])
        self.assertFalse(checker.feedback_applies_to_delivery(self.pending, self.pending["delivery"]))

    def test_all_three_explicit_choices_are_valid(self):
        for choice in ("accepted", "adjust", "off_target"):
            with self.subTest(choice=choice):
                doc = self.answered(choice)
                self.assertEqual(checker.validate_feedback_record(doc), [])
                self.assertTrue(checker.feedback_applies_to_delivery(doc, doc["delivery"]))

    def test_pending_cannot_smuggle_an_acceptance(self):
        doc = self.answered()
        doc["feedback"]["status"] = "pending"
        self.assertIn("Unanswered feedback must not contain an inferred response",
                      checker.validate_feedback_record(doc))

    def test_assistant_cannot_record_its_own_satisfaction(self):
        doc = self.answered()
        doc["feedback"]["response"]["source"] = "assistant"
        self.assertIn("Feedback needs an explicit user source and response time",
                      checker.validate_feedback_record(doc))

    def test_response_cannot_be_attached_to_another_delivery(self):
        doc = self.answered()
        doc["feedback"]["response"]["delivery_sha256"] = "0" * 64
        self.assertIn("Response belongs to another delivery", checker.validate_feedback_record(doc))

    def test_old_feedback_is_history_when_versions_or_content_change(self):
        doc = self.answered()
        variants = {"requirements_revision": 2, "artifact_revision": 2,
                    "requirements_sha256": "0" * 64, "content_sha256": "1" * 64}
        for field, value in variants.items():
            with self.subTest(field=field):
                current = copy.deepcopy(doc["delivery"])
                current[field] = value
                self.assertEqual(checker.validate_feedback_record(doc), [])
                self.assertFalse(checker.feedback_applies_to_delivery(doc, current))

    def test_edited_file_hash_does_not_inherit_acceptance(self):
        doc = self.answered()
        current = copy.deepcopy(doc["delivery"])
        current["artifacts"] = [{"path": "new-version.txt", "sha256": "2" * 64}]
        self.assertFalse(checker.feedback_applies_to_delivery(doc, current))

    def test_acceptance_preserves_failed_verification_and_permissions(self):
        doc = self.answered()
        doc["objective_verification"]["status"] = "failed"
        doc["permissions"] = {"run_model": False, "publish": False}
        doc["submission"] = None
        before = copy.deepcopy(doc)
        self.assertTrue(checker.feedback_applies_to_delivery(doc, doc["delivery"]))
        self.assertEqual(doc, before)
        self.assertEqual(doc["objective_verification"]["status"], "failed")

    def test_casual_questions_and_progress_do_not_trigger_prompts(self):
        self.assertFalse(checker.should_offer_feedback(important=False, delivered=True))
        self.assertFalse(checker.should_offer_feedback(important=True, delivered=False))

    def test_important_delivery_is_prompted_once(self):
        self.assertTrue(checker.should_offer_feedback(important=True, delivered=True))
        self.assertFalse(checker.should_offer_feedback(important=True, delivered=True, already_prompted=True))
        self.assertFalse(checker.should_offer_feedback(important=True, delivered=True,
                                                       explicit_feedback_received=True))

    def test_skip_is_allowed_without_inventing_a_response(self):
        doc = copy.deepcopy(self.pending)
        doc["feedback"]["status"] = "skipped"
        self.assertEqual(checker.validate_feedback_record(doc), [])
        self.assertFalse(checker.feedback_applies_to_delivery(doc, doc["delivery"]))


if __name__ == "__main__":
    unittest.main()

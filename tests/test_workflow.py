"""Meaningful invariants of the reference workflow, with temporary local artifacts."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("checker", ROOT / "tools/check_blueprint.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
EXAMPLE = ROOT / "examples/courses/DADS6003/Assignments/NN_homework/assignment-context.json"

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.artifact = self.root / "submission" / "demo.pdf"
        self.artifact.parent.mkdir()
        # A fake payload verifies identity mechanics, not PDF rendering/content.
        self.artifact.write_bytes(b"fictional artifact for contract testing")
        self.evidence = self.root / "verification.json"

    def tearDown(self):
        self.temp.cleanup()

    def ready_document(self):
        doc = copy.deepcopy(self.doc)
        doc["status"] = "ready_to_submit"
        doc["artifacts"] = [{"path": "submission/demo.pdf",
                             "sha256": checker.sha256(self.artifact),
                             "revision": doc["artifact_revision"]}]
        doc["verification"] = {"passed": True,
                               "requirements_revision": doc["requirements_revision"],
                               "artifact_revision": doc["artifact_revision"],
                               "requirements_sha256": checker.requirements_sha256(doc["current_requirements"]),
                               "evidence": ["verification.json"]}
        self.write_evidence({"passed": True,
                             "requirements_revision": doc["requirements_revision"],
                             "artifact_revision": doc["artifact_revision"],
                             "requirements_sha256": doc["verification"]["requirements_sha256"],
                             "artifact_sha256": doc["artifacts"][0]["sha256"]})
        return doc

    def write_evidence(self, report):
        self.evidence.write_text(json.dumps(report), encoding="utf-8")

    def edit_evidence(self, **updates):
        report = json.loads(self.evidence.read_text(encoding="utf-8"))
        report.update(updates)
        self.write_evidence(report)

    def test_draft_example_is_valid(self):
        self.assertEqual(checker.validate_assignment(self.doc, self.root), [])

    def test_readiness_requires_real_artifact_and_verification(self):
        self.doc["status"] = "in_review"
        self.assertTrue(checker.transition_errors(self.doc, "ready_to_submit", self.root))

    def test_verified_current_artifact_can_be_ready(self):
        self.assertEqual(checker.validate_assignment(self.ready_document(), self.root), [])

    def test_changed_requirements_invalidate_readiness(self):
        doc = self.ready_document()
        doc["requirements_revision"] += 1
        self.assertIn("Verification is stale: requirements_revision",
                      checker.validate_assignment(doc, self.root))

    def test_changed_requirements_without_revision_bump_are_rejected(self):
        doc = self.ready_document()
        doc["current_requirements"]["decimal_places"] = 2
        errors = checker.validate_assignment(doc, self.root)
        self.assertIn("Requirements content changed after verification", errors)
        self.assertIn("Evidence bound to different requirements", errors)

    def test_updating_only_metadata_hash_does_not_reuse_old_evidence(self):
        doc = self.ready_document()
        doc["current_requirements"]["decimal_places"] = 2
        doc["verification"]["requirements_sha256"] = checker.requirements_sha256(doc["current_requirements"])
        self.assertIn("Evidence bound to different requirements",
                      checker.validate_assignment(doc, self.root))

    def test_json_key_order_does_not_change_requirement_identity(self):
        doc = self.ready_document()
        doc["current_requirements"] = dict(reversed(list(doc["current_requirements"].items())))
        self.assertEqual(checker.validate_assignment(doc, self.root), [])

    def test_requirement_fingerprint_matches_live_encoding(self):
        import hashlib
        requirements = {"language": "\u0e20\u0e32\u0e29\u0e32\u0e44\u0e17\u0e22", "sections": ["\u0e42\u0e08\u0e17\u0e22\u0e4c", "\u0e27\u0e34\u0e18\u0e35\u0e17\u0e33"]}
        payload = json.dumps(requirements, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.assertEqual(checker.requirements_sha256(requirements),
                         hashlib.sha256(payload.encode("utf-8")).hexdigest())

    def test_changed_artifact_revision_invalidates_verification(self):
        doc = self.ready_document()
        doc["artifact_revision"] += 1
        self.assertIn("Verification is stale: artifact_revision",
                      checker.validate_assignment(doc, self.root))

    def test_modified_file_invalidates_checksum(self):
        doc = self.ready_document()
        self.artifact.write_bytes(b"edited after verification")
        self.assertIn("Artifact checksum mismatch",
                      checker.validate_assignment(doc, self.root))

    def test_missing_file_invalidates_readiness(self):
        doc = self.ready_document()
        self.artifact.unlink()
        self.assertIn("Artifact file is missing",
                      checker.validate_assignment(doc, self.root))

    def test_missing_evidence_invalidates_readiness(self):
        doc = self.ready_document()
        self.evidence.unlink()
        self.assertIn("Verification evidence file is missing",
                      checker.validate_assignment(doc, self.root))

    def test_existing_plain_text_is_not_verification_evidence(self):
        doc = self.ready_document()
        self.evidence.write_text("passed", encoding="utf-8")
        self.assertTrue(checker.validate_assignment(doc, self.root))

    def test_failed_evidence_cannot_certify_readiness(self):
        doc = self.ready_document()
        self.edit_evidence(passed=False)
        self.assertIn("Evidence does not confirm a pass",
                      checker.validate_assignment(doc, self.root))

    def test_wrong_evidence_revision_is_rejected(self):
        for field in ("requirements_revision", "artifact_revision"):
            with self.subTest(field=field):
                doc = self.ready_document()
                self.edit_evidence(**{field: doc[field] + 1})
                self.assertIn(f"Evidence is stale: {field}",
                              checker.validate_assignment(doc, self.root))

    def test_evidence_for_another_file_is_rejected(self):
        doc = self.ready_document()
        self.edit_evidence(artifact_sha256="0" * 64)
        self.assertIn("Evidence bound to a different artifact",
                      checker.validate_assignment(doc, self.root))

    def test_malformed_evidence_hash_fails_without_crashing(self):
        doc = self.ready_document()
        self.edit_evidence(artifact_sha256={})
        self.assertIn("Evidence bound to a different artifact",
                      checker.validate_assignment(doc, self.root))

    def test_second_artifact_needs_its_own_matching_evidence(self):
        doc = self.ready_document()
        second = self.root / "submission" / "second.txt"
        second.write_text("Another fictional artifact", encoding="utf-8")
        doc["artifacts"].append({"path": "submission/second.txt", "sha256": checker.sha256(second),
                                 "revision": doc["artifact_revision"]})
        self.assertIn("Verification evidence does not cover every selected artifact",
                      checker.validate_assignment(doc, self.root))
        report = json.loads(self.evidence.read_text(encoding="utf-8"))
        report["artifact_sha256"] = checker.sha256(second)
        (self.root / "second-evidence.json").write_text(json.dumps(report), encoding="utf-8")
        doc["verification"]["evidence"].append("second-evidence.json")
        self.assertEqual(checker.validate_assignment(doc, self.root), [])

    def test_ready_does_not_mean_submitted(self):
        doc = self.ready_document()
        self.assertTrue(checker.transition_errors(doc, "submitted", self.root))
        self.assertEqual(doc["status"], "ready_to_submit")

    def test_submission_with_user_confirmation_and_evidence(self):
        doc = self.ready_document()
        doc["submission"] = {"confirmed_by_user": True,
                             "submitted_at": "2026-11-14T10:00:00+07:00",
                             "evidence": "https://example.org/submission/receipt"}
        self.assertEqual(checker.transition_errors(doc, "submitted", self.root), [])

    def test_cannot_skip_from_in_progress_to_submitted(self):
        self.assertTrue(checker.transition_errors(self.doc, "submitted", self.root))

    def test_path_cannot_escape_project(self):
        with self.assertRaises(ValueError):
            checker.resolve_under(self.root, "../private.txt")
        with self.assertRaises(ValueError):
            checker.resolve_under(self.root, "C:/private.txt")

    def test_nonportable_path_aliases_and_streams_are_rejected(self):
        for value in ("submission/demo.pdf:stream", "NUL.txt", "folder/../demo.pdf",
                      "submission//demo.pdf", "submission/demo.pdf.", "folder\\demo.pdf"):
            with self.subTest(path=value), self.assertRaises(ValueError):
                checker.resolve_under(self.root, value)

    def test_boolean_revisions_do_not_certify_ready_work(self):
        for record in ("verification", "artifact", "evidence"):
            with self.subTest(record=record):
                doc = self.ready_document()
                if record == "verification":
                    doc["verification"]["artifact_revision"] = True
                elif record == "artifact":
                    doc["artifacts"][0]["revision"] = True
                else:
                    self.edit_evidence(artifact_revision=True)
                self.assertTrue(checker.validate_assignment(doc, self.root))

    def test_malformed_workflow_state_reports_failure_without_crashing(self):
        self.doc["status"] = {"unexpected": "object"}
        self.assertIn("Unknown workflow state", checker.validate_assignment(self.doc, self.root))
        self.assertTrue(checker.transition_errors(self.doc, "in_progress", self.root))
        self.assertTrue(checker.transition_errors({}, [], self.root))

    def test_transition_does_not_mutate_source(self):
        doc = self.ready_document()
        before = copy.deepcopy(doc)
        checker.transition_errors(doc, "in_progress", self.root)
        self.assertEqual(doc, before)

    def test_registered_project_metadata_is_valid_without_execution(self):
        workspace = ROOT / "examples"
        registry = checker.read_json(workspace / "workspace.json")
        self.assertEqual(checker.validate_project(registry["projects"][0], workspace), [])

    def test_project_cannot_use_context_from_another_task(self):
        workspace = ROOT / "examples"
        project = checker.read_json(workspace / "workspace.json")["projects"][0]
        project["current_context"] = "courses/DADS6003/course-context.json"
        self.assertIn("Project context routing mismatch", checker.validate_project(project, workspace))

if __name__ == "__main__":
    unittest.main()

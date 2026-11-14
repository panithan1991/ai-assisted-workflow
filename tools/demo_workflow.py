"""Replay a fictional assignment in a temporary directory; no external actions."""
from __future__ import annotations
import copy
import json
import tempfile
from pathlib import Path

from check_blueprint import (ROOT, read_json, requirements_sha256, resolve_under,
                             sha256, transition_errors, validate_assignment)


def simulate_review(doc: dict, root: Path, artifact_path: str) -> dict:
    """Create synthetic review evidence, never a real content certification."""
    reviewed = copy.deepcopy(doc)
    reviewed["status"] = "in_review"
    checksum = sha256(resolve_under(root, artifact_path))
    fingerprint = requirements_sha256(reviewed["current_requirements"])
    evidence_path = f"review-v{reviewed['artifact_revision']}.json"
    report = {
        "passed": True,
        "requirements_revision": reviewed["requirements_revision"],
        "artifact_revision": reviewed["artifact_revision"],
        "requirements_sha256": fingerprint,
        "artifact_sha256": checksum,
        "fictional_example": True,
        "note": "Simulated review only; no academic content was assessed."
    }
    resolve_under(root, evidence_path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reviewed["artifacts"] = [{"path": artifact_path, "sha256": checksum,
                              "revision": reviewed["artifact_revision"]}]
    reviewed["verification"] = {
        "passed": True,
        "requirements_revision": reviewed["requirements_revision"],
        "artifact_revision": reviewed["artifact_revision"],
        "requirements_sha256": fingerprint,
        "evidence": [evidence_path]
    }
    errors = transition_errors(reviewed, "ready_to_submit", root)
    if errors:
        raise RuntimeError(errors)
    reviewed["status"] = "ready_to_submit"
    return reviewed


def run_demo() -> None:
    print("DEMO ONLY: fictional files and simulated review; no real submission.")
    doc = read_json(ROOT / "examples/walkthrough/assignment.json")
    with tempfile.TemporaryDirectory(prefix="learning-workflow-demo-") as directory:
        root = Path(directory).resolve()
        if not root.is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise RuntimeError("Unexpected temporary directory")
        if validate_assignment(doc, root):
            raise RuntimeError("Invalid draft example")
        print("1. PASS: draft has requirements and no selected artifact.")

        resolve_under(root, "answer-v1.txt").write_text(
            "Question: fictional task.\nMethod: fictional method.\nConclusion: fictional result.\n",
            encoding="utf-8")
        ready = simulate_review(doc, root, "answer-v1.txt")
        print("2. PASS: simulated review binds requirements and answer-v1.txt.")

        changed = copy.deepcopy(ready)
        changed["current_requirements"]["sections"].append("Limitations")
        if "Requirements content changed after verification" not in validate_assignment(changed, root):
            raise RuntimeError("Edited requirements incorrectly remained ready")
        print("3. EXPECTED REJECTION: changed requirements, even without a revision bump.")

        changed["status"] = "in_progress"
        changed["requirements_revision"] += 1
        changed["artifact_revision"] += 1
        changed["artifacts"] = []
        changed["verification"] = {"passed": False, "evidence": []}
        changed["next_actions"] = ["Add Limitations and review the new version."]
        if validate_assignment(changed, root):
            raise RuntimeError("Invalid revised draft")
        resolve_under(root, "answer-v2.txt").write_text(
            resolve_under(root, "answer-v1.txt").read_text(encoding="utf-8")
            + "Limitations: this is a synthetic example.\n", encoding="utf-8")
        ready_v2 = simulate_review(changed, root, "answer-v2.txt")
        print("4. PASS: revised answer-v2.txt reviewed; answer-v1.txt is preserved.")

        edited = resolve_under(root, "answer-v2.txt")
        original = edited.read_bytes()
        edited.write_bytes(original + b"Changed after review.\n")
        if "Artifact checksum mismatch" not in validate_assignment(ready_v2, root):
            raise RuntimeError("Edited artifact incorrectly remained ready")
        edited.write_bytes(original)
        print("5. EXPECTED REJECTION: artifact edited after review.")

        if not transition_errors(ready_v2, "submitted", root):
            raise RuntimeError("Submission without confirmation was accepted")
        print("6. EXPECTED REJECTION: ready does not mean submitted.")

        simulated = copy.deepcopy(ready_v2)
        simulated["submission"] = {
            "confirmed_by_user": True,
            "submitted_at": "2026-01-01T12:00:00+00:00",
            "evidence": "SIMULATED receipt only; no external action occurred."
        }
        if transition_errors(simulated, "submitted", root):
            raise RuntimeError("Valid simulated transition was rejected")
        print("7. PASS: simulated confirmation satisfies the contract; nothing was sent.")
    print("DONE: temporary demo files removed; repository examples unchanged.")


if __name__ == "__main__":
    run_demo()

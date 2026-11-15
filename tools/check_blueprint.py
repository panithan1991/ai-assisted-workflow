"""Reference checks for the architecture examples. Python 3.10+, stdlib only."""
from __future__ import annotations
import copy
import hashlib
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
STATES = {"inbox", "in_progress", "in_review", "ready_to_submit", "submitted", "archived"}
TRANSITIONS = {
    "inbox": {"in_progress"},
    "in_progress": {"in_review"},
    "in_review": {"in_progress", "ready_to_submit"},
    "ready_to_submit": {"in_progress", "submitted"},
    "submitted": {"in_progress", "archived"},
    "archived": set(),
}
READY_STATES = {"ready_to_submit", "submitted", "archived"}
FEEDBACK_CHOICES = {"accepted", "adjust", "off_target"}


def portable_relative_path(value: str) -> PurePosixPath:
    """Reject platform-dependent aliases, streams and escaping path syntax."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Use a nonempty portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or not path.parts:
        raise ValueError("Use a canonical portable relative path")
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{n}" for n in range(1, 10)),
                *(f"LPT{n}" for n in range(1, 10))}
    for part in path.parts:
        if (part in {".", ".."} or part.rstrip(" .") != part
                or re.search(r'[<>:"|?*\x00-\x1f]', part)
                or part.split(".", 1)[0].upper() in reserved):
            raise ValueError("Path contains a nonportable or escaping component")
    return path


def should_offer_feedback(*, important: bool, delivered: bool,
                          already_prompted: bool = False,
                          explicit_feedback_received: bool = False) -> bool:
    """Cadence rule only; the caller classifies the task and delivers the work."""
    return important and delivered and not already_prompted and not explicit_feedback_received


def delivery_sha256(delivery: dict) -> str:
    return requirements_sha256(delivery)


def validate_feedback_record(doc: dict) -> list[str]:
    """Validate feedback metadata; never change verification or permissions."""
    if not isinstance(doc, dict):
        return ["Feedback record must be an object"]
    errors = []
    if doc.get("schema_version") != "1.0" or doc.get("kind") != "feedback_record":
        errors.append("Unsupported feedback contract")
    delivery = doc.get("delivery")
    if not isinstance(delivery, dict):
        return errors + ["Delivery snapshot is required"]
    for field in ("delivery_id", "task_id"):
        if not isinstance(delivery.get(field), str) or not delivery[field].strip():
            errors.append(f"Missing delivery field: {field}")
    for field in ("requirements_revision", "artifact_revision"):
        if type(delivery.get(field)) is not int or delivery[field] < 1:
            errors.append(f"Invalid delivery revision: {field}")
    def valid_hash(value):
        return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None
    if not valid_hash(delivery.get("requirements_sha256")):
        errors.append("Delivery requirements fingerprint is required")
    artifacts = delivery.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("Delivery artifacts must be a list")
    else:
        for artifact in artifacts:
            if not isinstance(artifact, dict) or not valid_hash(artifact.get("sha256")):
                errors.append("Invalid delivery artifact fingerprint")
                continue
            path = artifact.get("path")
            try:
                portable_relative_path(path)
            except ValueError:
                errors.append("Delivery artifact path must be portable and relative")
        if not artifacts and not valid_hash(delivery.get("content_sha256")):
            errors.append("Inline delivery needs a content fingerprint")
    try:
        fingerprint = delivery_sha256(delivery)
    except (TypeError, ValueError):
        return errors + ["Delivery snapshot must contain portable JSON values"]
    if doc.get("delivery_sha256") != fingerprint:
        errors.append("Delivery snapshot fingerprint mismatch")
    objective = doc.get("objective_verification")
    if not isinstance(objective, dict) or objective.get("status") not in (
            "passed", "failed", "not_checked", "not_applicable"):
        errors.append("Explicit objective verification status is required")
    feedback = doc.get("feedback")
    if not isinstance(feedback, dict):
        return errors + ["Feedback state is required"]
    state = feedback.get("status")
    response = feedback.get("response")
    if state in ("pending", "skipped"):
        if response is not None:
            errors.append("Unanswered feedback must not contain an inferred response")
    elif state == "responded":
        if not isinstance(response, dict):
            return errors + ["Explicit user response is required"]
        if not isinstance(response.get("choice"), str) or response["choice"] not in FEEDBACK_CHOICES:
            errors.append("Unknown feedback choice")
        if response.get("source") != "user" or not response.get("received_at"):
            errors.append("Feedback needs an explicit user source and response time")
        if response.get("delivery_sha256") != fingerprint:
            errors.append("Response belongs to another delivery")
    else:
        errors.append("Unknown feedback state")
    return errors


def feedback_applies_to_delivery(doc: dict, current_delivery: dict) -> bool:
    """Old feedback remains history; no acceptance is copied to a new snapshot."""
    if validate_feedback_record(doc) or doc["feedback"]["status"] != "responded":
        return False
    try:
        return isinstance(current_delivery, dict) and doc["delivery_sha256"] == delivery_sha256(current_delivery)
    except (TypeError, ValueError):
        return False

def resolve_under(root: Path, relative: str) -> Path:
    """Only portable relative paths that resolve inside this root are allowed."""
    portable_relative_path(relative)
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ValueError("Path escapes its declared root")
    return candidate

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def requirements_sha256(requirements: dict) -> str:
    """Match the live workspace's canonical JSON fingerprint."""
    payload = json.dumps(requirements, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def validate_assignment(doc: dict, project_root: Path | None = None) -> list[str]:
    if not isinstance(doc, dict):
        return ["Assignment must be an object"]
    errors = []
    required = ["schema_version", "kind", "id", "course_id", "status",
                "requirements_revision", "artifact_revision", "current_requirements",
                "sources", "artifacts", "verification", "submission", "next_actions"]
    for field in required:
        if field not in doc:
            errors.append(f"Missing field: {field}")
    if errors:
        return errors
    if doc["schema_version"] != "1.0" or doc["kind"] != "assignment":
        errors.append("Unsupported assignment contract")
    if not all(isinstance(doc[k], str) and doc[k].strip() for k in ("id", "course_id")):
        errors.append("Assignment and course identifiers must be nonempty strings")
    for field in ("requirements_revision", "artifact_revision"):
        if type(doc[field]) is not int or doc[field] < 1:
            errors.append(f"{field} must be a positive integer")
    requirements_valid = isinstance(doc["current_requirements"], dict) and bool(doc["current_requirements"])
    if not requirements_valid:
        errors.append("Current requirements must be a nonempty object")
    if not isinstance(doc["sources"], list) or not doc["sources"]:
        errors.append("At least one source reference is required")
    if not isinstance(doc["next_actions"], list):
        errors.append("next_actions must be a list")
    if not isinstance(doc["artifacts"], list):
        errors.append("artifacts must be a list")
        return errors
    if not isinstance(doc["verification"], dict):
        errors.append("verification must be an object")
        return errors
    state = doc["status"]
    if not isinstance(state, str) or state not in STATES:
        errors.append("Unknown workflow state")
        return errors
    if state in READY_STATES:
        if not doc["artifacts"]:
            errors.append("A ready assignment requires an artifact")
        verification = doc["verification"]
        if verification.get("passed") is not True:
            errors.append("Verification has not passed")
        requirements_hash = None
        if requirements_valid:
            try:
                requirements_hash = requirements_sha256(doc["current_requirements"])
            except (TypeError, ValueError):
                errors.append("Current requirements must contain portable JSON values")
            if verification.get("requirements_sha256") != requirements_hash:
                errors.append("Requirements content changed after verification")
        for field in ("requirements_revision", "artifact_revision"):
            if type(verification.get(field)) is not int or verification[field] != doc[field]:
                errors.append(f"Verification is stale: {field}")
        evidence = verification.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append("Verification evidence is required")
        if project_root is None:
            errors.append("Artifact root is required to verify files")
        artifact_hashes = set()
        for artifact in doc["artifacts"]:
            if not isinstance(artifact, dict):
                errors.append("Artifact records must be objects")
                continue
            if type(artifact.get("revision")) is not int or artifact["revision"] != doc["artifact_revision"]:
                errors.append("Artifact revision is stale")
            checksum = artifact.get("sha256", "")
            if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
                errors.append("Artifact SHA-256 is required")
            else:
                artifact_hashes.add(checksum)
            if project_root is not None:
                try:
                    file = resolve_under(project_root, artifact.get("path", ""))
                    if not file.is_file():
                        errors.append("Artifact file is missing")
                    elif checksum != sha256(file):
                        errors.append("Artifact checksum mismatch")
                except (ValueError, OSError) as exc:
                    errors.append(str(exc))
        covered_hashes = set()
        if project_root is not None and isinstance(evidence, list):
            for entry in evidence:
                try:
                    evidence_path = resolve_under(project_root, entry)
                    if not evidence_path.is_file():
                        errors.append("Verification evidence file is missing")
                        continue
                    report = read_json(evidence_path)
                    if report.get("passed") is not True:
                        errors.append("Evidence does not confirm a pass")
                    if requirements_hash is None or report.get("requirements_sha256") != requirements_hash:
                        errors.append("Evidence bound to different requirements")
                    for field in ("requirements_revision", "artifact_revision"):
                        if type(report.get(field)) is not int or report[field] != doc[field]:
                            errors.append(f"Evidence is stale: {field}")
                    if not isinstance(report.get("artifact_sha256"), str) or report["artifact_sha256"] not in artifact_hashes:
                        errors.append("Evidence bound to a different artifact")
                    else:
                        covered_hashes.add(report["artifact_sha256"])
                except (ValueError, OSError, UnicodeError) as exc:
                    errors.append(str(exc))
            if artifact_hashes - covered_hashes:
                errors.append("Verification evidence does not cover every selected artifact")
    if state in {"submitted", "archived"}:
        submission = doc["submission"]
        if not isinstance(submission, dict):
            errors.append("Submission evidence is required")
        elif (submission.get("confirmed_by_user") is not True
              or not submission.get("submitted_at")
              or not submission.get("evidence")):
            errors.append("Submission needs user confirmation, time, and evidence")
    return errors

def transition_errors(doc: dict, target: str,
                      project_root: Path | None = None) -> list[str]:
    """Validate a proposed transition; never write state or perform submission."""
    if not isinstance(doc, dict) or not isinstance(doc.get("status"), str) or not isinstance(target, str):
        return ["Transition requires string source and target states"]
    if target not in TRANSITIONS.get(doc.get("status"), set()):
        return [f"Transition not allowed: {doc.get('status')} -> {target}"]
    candidate = copy.deepcopy(doc)
    candidate["status"] = target
    return validate_assignment(candidate, project_root)

def read_json(path: Path) -> dict:
    def reject_constant(value):
        raise ValueError(f"{path.name}: nonfinite JSON number {value} is not portable")
    value = json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: expected object")
    return value

def validate_project(project: dict, workspace_root: Path) -> list[str]:
    """Resolve metadata only; never import or execute the registered project."""
    errors = []
    for field in ("id", "path", "entry"):
        if not isinstance(project.get(field), str) or not project[field].strip():
            errors.append(f"Missing project field: {field}")
    if errors:
        return errors
    try:
        if not resolve_under(workspace_root, project["path"]).exists():
            errors.append("Project path is missing")
        if not resolve_under(workspace_root, project["entry"]).is_file():
            errors.append("Project entry is missing")
        if project.get("instructions") and not resolve_under(workspace_root, project["instructions"]).is_file():
            errors.append("Project instructions are missing")
        if project.get("current_context"):
            context = read_json(resolve_under(workspace_root, project["current_context"]))
            if context.get("project_id") != project["id"] or context.get("course_id") != project.get("course_id"):
                errors.append("Project context routing mismatch")
        for relative in project.get("references", []):
            if not resolve_under(workspace_root, relative).is_file():
                errors.append("Project reference is missing")
    except (ValueError, OSError, UnicodeError) as exc:
        errors.append(str(exc))
    return errors


def markdown_lines(text: str):
    """Yield prose lines, excluding fenced code blocks."""
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield line


def markdown_targets(text: str):
    """Read inline destinations and reference definitions, not code examples."""
    for line in markdown_lines(text):
        line = re.sub(r"(`+).*?\1", "", line)
        for match in re.finditer(
                r'!?\[[^\]\n]*\]\(\s*(?:<([^>\n]*)>|((?:[^()\s]|\([^()]*\))+))'
                r'(?:\s+[\"\'][^\n]*?[\"\'])?\s*\)', line):
            yield match.group(1) if match.group(1) is not None else match.group(2)
        reference = re.match(r'^\s{0,3}\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))', line)
        if reference:
            yield reference.group(1) or reference.group(2)


def markdown_anchors(text: str) -> set[str]:
    """Resolve ordinary GitHub-style heading anchors and explicit HTML ids."""
    anchors, counts = set(), {}
    for line in markdown_lines(text):
        anchors.update(re.findall(r'<a\s+[^>]*(?:id|name)=[\"\']([^\"\']+)', line, re.I))
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading:
            continue
        title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading.group(1))
        title = re.sub(r"<[^>]*>", "", title).lower()
        slug = re.sub(r"[^\w\-\s]", "", title)
        slug = re.sub(r"\s", "-", slug)
        suffix = counts.get(slug, 0)
        counts[slug] = suffix + 1
        anchors.add(slug if suffix == 0 else f"{slug}-{suffix}")
    return anchors


def check_markdown_links(root: Path, paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        for target in markdown_targets(path.read_text(encoding="utf-8-sig")):
            parsed = urlsplit(target)
            if parsed.scheme in {"http", "https", "mailto"}:
                continue
            if parsed.scheme or parsed.netloc or parsed.path.startswith("/") or "\\" in parsed.path:
                errors.append(f"{path.relative_to(root)}: nonportable local link {target}")
                continue
            candidate = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path.resolve()
            if not candidate.is_relative_to(root.resolve()) or not candidate.exists():
                errors.append(f"{path.relative_to(root)}: broken local link {target}")
            elif parsed.fragment and candidate.suffix.lower() == ".md":
                if unquote(parsed.fragment) not in markdown_anchors(candidate.read_text(encoding="utf-8-sig")):
                    errors.append(f"{path.relative_to(root)}: missing heading anchor {target}")
    return errors


def public_package_files(root: Path) -> tuple[list[Path], list[str]]:
    """Check this text-only template package without reading private directories."""
    paths, errors = [], []
    ignored = {".git", "__pycache__", ".pytest_cache"}
    private = {"_workspace", "_local", "private", "data", "models", "outputs", "raw", "clippings",
               ".obsidian", ".codex", ".venv", "venv", "node_modules"}
    extensions = {".md", ".json", ".py", ".yml", ".yaml", ".toml", ".txt"}
    for directory, folders, files in os.walk(root, followlinks=False):
        current = Path(directory)
        keep = []
        for name in folders:
            path = current / name
            if name in ignored:
                continue
            attributes = getattr(path.lstat(), "st_file_attributes", 0)
            if path.is_symlink() or attributes & 0x400:
                errors.append(f"{path.relative_to(root)}: linked directories cannot be published")
            elif name.lower() in private:
                errors.append(f"{path.relative_to(root)}: private/runtime directory is not a public template")
            else:
                keep.append(name)
        folders[:] = keep
        for name in files:
            path = current / name
            relative = path.relative_to(root)
            lowered = name.lower()
            if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
                errors.append(f"{relative}: linked files cannot be published")
                continue
            if ((lowered.startswith(".env") and lowered != ".env.example")
                    or lowered in {"secrets.toml", "credentials.json", "desktop.ini", ".ds_store"}):
                errors.append(f"{relative}: private configuration cannot be published")
                continue
            if path.suffix.lower() not in extensions and name not in {"LICENSE", ".gitignore", ".env.example"}:
                errors.append(f"{relative}: unexpected file type in this text-only blueprint")
                continue
            if path.stat().st_size > 1024 * 1024:
                errors.append(f"{relative}: unexpectedly large public text file")
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except UnicodeError:
                errors.append(f"{relative}: public text must be UTF-8")
                continue
            if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", text):
                errors.append(f"{relative}: private-key material detected")
            if re.search(r"\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{30,})", text):
                errors.append(f"{relative}: possible access token detected")
            paths.append(path)
    return paths, errors

def check_repository(root: Path = ROOT) -> list[str]:
    public_files, errors = public_package_files(root)
    if errors:
        return errors
    examples = root / "examples"
    for path in examples.rglob("*.json"):
        doc = read_json(path)
        if doc.get("schema_version") != "1.0" or not doc.get("kind"):
            errors.append(f"{path.relative_to(root)}: invalid contract header")
        if doc.get("kind") == "feedback_record":
            errors.extend(f"{path.relative_to(root)}: {error}" for error in validate_feedback_record(doc))
    registry = read_json(examples / "workspace.json")
    environments = read_json(examples / "environments.json")
    environment_ids = [e["id"] for e in environments["environments"]]
    if len(environment_ids) != len(set(environment_ids)):
        errors.append("Duplicate environment id")
    ids = [c["id"] for c in registry["courses"]]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate course id")
    projects = registry.get("projects", [])
    projects_by_id = {project["id"]: project for project in projects}
    if len(projects_by_id) != len(projects):
        errors.append("Duplicate project id")
    for project in projects:
        if project.get("course_id") is not None and project["course_id"] not in ids:
            errors.append(f"Unknown project course: {project['id']}")
        errors.extend(f"{project['id']}: {error}" for error in validate_project(project, examples))
    for course in registry["courses"]:
        path = resolve_under(examples, course["context"])
        doc = read_json(path)
        if doc.get("id") != course["id"]:
            errors.append(f"Course id mismatch: {course['id']}")
        for project_id in doc.get("project_ids", []):
            project = projects_by_id.get(project_id)
            if project is None:
                errors.append(f"Unknown course project: {project_id}")
            elif project.get("course_id") != course["id"]:
                errors.append(f"Course project routing mismatch: {project_id}")
        for environment in doc.get("environment_ids", []):
            if environment not in environment_ids:
                errors.append(f"Unknown environment: {environment}")
        for task in doc.get("assignments", []):
            task_path = resolve_under(path.parent, task["context"])
            assignment = read_json(task_path)
            if assignment.get("id") != task["id"] or assignment.get("course_id") != course["id"]:
                errors.append(f"Task routing mismatch: {task['id']}")
            errors.extend(f"{task['id']}: {e}" for e in
                          validate_assignment(assignment, task_path.parent))
            history = read_json(resolve_under(task_path.parent, assignment["history"]))
            latest = max(history["events"], key=lambda event: event["revision"])
            if latest["revision"] != assignment["requirements_revision"]:
                errors.append(f"History revision mismatch: {task['id']}")
            if assignment["current_requirements"].get(latest["field"]) != latest["value"]:
                errors.append(f"Current requirement disagrees with history: {task['id']}")
    errors.extend(check_markdown_links(root, [path for path in public_files if path.suffix == ".md"]))
    return errors

if __name__ == "__main__":
    try:
        errors = check_repository()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
    if errors:
        print("\n".join(f"FAIL: {e}" for e in errors), file=sys.stderr)
        sys.exit(1)
    print("PASS: public package, example routing, project references, assignment contracts, history, and documentation links")

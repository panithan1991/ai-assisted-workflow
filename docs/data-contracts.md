# Data contracts

A data contract defines what a record contains, who maintains it, and which record other parts of the workflow should trust. The reference checker implements the core invariants described here; it does not evaluate the academic or practical quality of the work itself.

## One owner for each fact

- The workspace index stores paths, not duplicate assignment requirements or submission status.
- A course record stores course context and task references.
- An assignment record owns current requirements, state, and selected artifacts.
- Verification refers to specific requirements and artifact versions.
- History retains earlier events and does not become the default current context.

In an existing workspace, the index can point directly to a record under a private state directory. Do not assume that every file named `assignment-context.json` is authoritative when legacy scripts or copies exist.

## Assignment fields

| Field | Meaning |
|---|---|
| `schema_version` | Version of the record format |
| `kind` | Record type; `assignment` for this contract |
| `id`, `course_id` | Stable IDs, independent of display names |
| `status` | `inbox`, `in_progress`, `in_review`, `ready_to_submit`, `submitted`, or `archived` |
| `requirements_revision` | Current requirements version; increment when confirmed scope changes |
| `artifact_revision` | Current output version; increment when selected deliverable content changes |
| `current_requirements` | Only current requirements, excluding superseded instructions |
| `sources` | Evidence for the original task and confirmed corrections |
| `artifacts` | Selected files with paths, SHA-256 hashes, and revisions |
| `verification` | Review result, version bindings, and evidence references |
| `submission` | Evidence of an actual submission, or `null` |
| `next_actions` | Remaining work |

See the [fictional assignment](../examples/courses/DADS6003/Assignments/NN_homework/assignment-context.json) for a working example. Course IDs in examples are illustrative and can be replaced in an adopted workspace.

## Readiness conditions

`ready_to_submit` requires:

- A nonempty artifact list, with every file at the current artifact revision.
- A path and SHA-256 hash for each selected file.
- `verification.passed` set to `true` after an appropriate review.
- Matching requirements and artifact revisions in the verification record.
- A `verification.requirements_sha256` matching the current requirements content, even if somebody forgot to increment its revision.
- Readable JSON evidence confirming the same requirements, revisions, and selected files.

`submitted` and `archived` must satisfy those same checks and include a submission record with user confirmation, a time, and evidence. A ready PDF and an approving feedback response do not establish submission.

An artifact revision change invalidates previous verification just as a requirements change does.

### Requirements identity

The checker hashes a deterministic JSON representation:

~~~python
payload = json.dumps(current_requirements, ensure_ascii=False,
                     sort_keys=True, separators=(",", ":"), allow_nan=False)
requirements_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
~~~

Use valid JSON values, without `NaN` or infinity. Reordering object keys does not change this hash; changing a value, section list, or required precision does. A changed hash does not replace the normal requirement to increment the revision and verify the updated work.

### Verification evidence

Each evidence file is a JSON object with these bindings:

| Field | Required meaning |
|---|---|
| `passed` | `true` after the task's acceptance criteria have been checked |
| `requirements_revision` | Current requirements revision |
| `artifact_revision` | Current artifact revision |
| `requirements_sha256` | Hash of the reviewed current requirements |
| `artifact_sha256` | Hash of one selected artifact |

When several artifacts are selected, the evidence listed in `verification.evidence` must cover every file. A text file containing only "passed", or evidence from another assignment, is insufficient.

The checker reads recorded evidence. It cannot prove who performed the review or whether the content was reviewed competently. In the [demo](walkthrough.md), `passed=true` is simulated to demonstrate the contract, not to certify a real deliverable.

## Project registry

The workspace `projects` list stores `id`, `course_id`, `path`, and `entry`, with optional `current_context`, `instructions`, and `references`. Paths are relative to the example workspace root.

Course records refer to projects through `project_ids`. The checker verifies course IDs, project IDs, and referenced local paths. For example, `project_id` in a project's context must match its index entry. Registration checks do not import project code, train a model, or start a service.

The [transaction project](../examples/projects/transaction-demo/README.md) illustrates a project whose experiment choices still require a user decision.

## Feedback record

Feedback is separate from the assignment contract. Skipping feedback does not make an otherwise verified deliverable unready. See the [fictional pending record](../examples/feedback/pending.json) and [feedback workflow](feedback-loop.md).

- `delivery` identifies the delivery and task, requirements revision/hash, artifact revision, and artifact path/hash pairs. A chat-only answer can use `content_sha256` instead of file artifacts.
- `delivery_sha256` hashes the deterministic JSON form of `delivery`. Build the snapshot from the actual delivered files or text; compare it with the current delivery before reusing feedback.
- `objective_verification.status` is `passed`, `failed`, `not_checked`, or `not_applicable`. Evidence-based checking is separate from user satisfaction.
- `feedback.status` is `pending`, `responded`, or `skipped`. Pending and skipped feedback have `response=null`.
- A response has a `choice` of `accepted`, `adjust`, or `off_target`, with `source=user`, `received_at`, and a `delivery_sha256` matching the delivery the user evaluated.

The feedback checker validates the record and the internal consistency of its snapshot. It does not authenticate the user response or prove that current files still match the snapshot. The recorder must retain explicit user input and compare actual current files when that matters. Assignment verification remains responsible for checking artifacts and evidence.

Feedback on an earlier delivery remains valid history. `feedback_applies_to_delivery` returns `false` for a different delivery snapshot. Acceptance does not convert failed verification into a pass, mark an assignment submitted, or authorize model runs or publication.

Keep real feedback and its policy in private workspace state. Public examples must remain fictional.

## Portable examples and private configuration

Public examples use relative paths and fictional values. Keep real interpreter locations, service endpoints, credentials, and private project state in a local configuration layer outside the public repository.

`is_cuda_available` records a test in the selected environment, not a CUDA version copied from driver output. If the environment has not been checked, leave the result `null` and `verified=false`.

## Checker scope

`tools/check_blueprint.py` is a small reference implementation. It checks assignment invariants, course and project references, supported state transitions, and fictional feedback records. For readiness checks with an artifact root, it reads actual selected files, their hashes, and JSON evidence under that root.

The supplied assignment starts `in_progress` without selected artifacts. It does not claim to include a reviewed submission PDF. The checker does not open source URLs, call AI, evaluate domain facts, or perform a real submission. Real use still needs calculations, execution tests, source review, or rendered-document inspection appropriate to the task.

A matching SHA-256 hash establishes that bytes are unchanged. It does not establish that their content is correct.

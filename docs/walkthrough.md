# Walk through one assignment

This example follows a fictional DEMO101 report from its first requirements to simulated submission confirmation. It uses no student report, real course data, or service account. Review results and submission confirmation are simulated.

Use Python 3.10 or later. From the repository root, run:

~~~sh
python -B tools/demo_workflow.py
~~~

The program reads the [fictional task](../examples/walkthrough/assignment.json) and works in a temporary directory. It does not change the example, call AI, train a model, or transmit data. It removes its own temporary demo files when finished.

## 1. Record the current task

The first version requires Question, Method, and Conclusion sections. The record stores these in `current_requirements`, with `requirements_revision=1` and `status=in_progress`. It has no selected artifact and makes no review claim.

To resume the task later, read the current requirements, sources, artifact version, and `next_actions`. Chat history should not be the only source of current requirements.

## 2. Create a draft and simulate review

The demo creates `answer-v1.txt`. A simulated reviewer writes JSON evidence containing `passed=true`, requirements and artifact revisions, `requirements_sha256`, and `artifact_sha256`.

The checker reads the actual answer and evidence before accepting a transition from `in_review` to `ready_to_submit`. Setting a metadata flag without matching evidence is insufficient.

In real work, verify the content, calculations, execution, or layout before recording a pass. The demo demonstrates the record contract; it does not assess academic quality.

## 3. Change a requirement after review

The demo adds a Limitations section to `current_requirements` without incrementing the revision. Readiness must be rejected because the requirements hash no longer matches.

This shows why the record uses both versions and hashes: the revision communicates the change history, while the hash detects changed content even when a revision update was missed.

## 4. Revise and review again

The demo returns to `in_progress`, increments both revisions to 2, and creates `answer-v2.txt` with Limitations. It preserves `answer-v1.txt` and creates fresh simulated evidence bound to the new hashes.

Readiness is accepted again only when all bindings match. The checker does not update states or revisions automatically; the demo performs those changes explicitly.

## 5. Change a file after review

The demo modifies `answer-v2.txt` and checks it again. The checker must reject it because the file hash differs from the reviewed version. The demo then restores the original bytes of that temporary file.

In real work, a changed selected deliverable needs a new artifact revision and review. Renaming a file to include "final" does not establish readiness.

## 6. Distinguish ready from submitted

A transition to `submitted` without submission evidence must be rejected. The demo then supplies a fictional user confirmation, timestamp, and receipt description, so the simulated record satisfies the contract.

This does not send a file or verify a receipt with a submission website. A real task needs actual user-confirmed evidence before recording `submitted`.

## Expected output

~~~text
DEMO ONLY: fictional files and simulated review; no real submission.
1. PASS: draft has requirements and no selected artifact.
2. PASS: simulated review binds requirements and answer-v1.txt.
3. EXPECTED REJECTION: changed requirements, even without a revision bump.
4. PASS: revised answer-v2.txt reviewed; answer-v1.txt is preserved.
5. EXPECTED REJECTION: artifact edited after review.
6. EXPECTED REJECTION: ready does not mean submitted.
7. PASS: simulated confirmation satisfies the contract; nothing was sent.
DONE: temporary demo files removed; repository examples unchanged.
~~~

`EXPECTED REJECTION` is a successful demonstration of a guard. The program should exit with code 0 when the example behaves as intended.

## Apply it to your own workspace

Begin with an index pointing to existing folders, choose one current record for the task, and apply the contract to that task first. Keep machine-specific configuration outside the public repository.

For a project that still needs user-selected experiment choices, see [transaction-demo](../examples/projects/transaction-demo/README.md). Its entries show README, context, instructions, and source references without invoking a trainer or starting a service.

# Verification and feedback

Use this loop for important deliverables: reports, completed code changes, requested study materials, folder maintenance, and project milestones. Skip it for casual questions, short explanations, progress updates, and intermediate steps.

This is a working agreement between the user and assistant. The assistant must read the policy used in its workspace. The loop does not run as a background service, retrain a model, or synchronize memory across applications.

~~~mermaid
flowchart TD
    A["Define success from the current request"] --> B["Work within the authorized scope"]
    B --> C["Verify with appropriate evidence"]
    C -->|"Problem found"| D["Investigate, fix, and recheck affected work"]
    D --> C
    C --> E["Deliver with checks and limitations"]
    E -->|"Important deliverable"| F["Offer three optional feedback choices"]
    E -->|"Casual question"| G["Finish without a feedback prompt"]
    F -->|"Adjust or off target"| D
    F -->|"Accepted"| H["Record feedback for this delivery"]
    F -->|"No answer"| I["Keep pending; do not remind"]
    F -->|"Explicitly skipped"| J["Record skipped"]
~~~

## Before and during work

Define success using the current request and confirmed requirements. Do not ask again when the answer is already clear. Match verification to the task:

- Calculations and interpretation for statistical work.
- Execution and meaningful results for code.
- Page count and rendered-page inspection for a document.
- Links and original-file hashes for folder maintenance.

Record verification as `passed`, `failed`, `not_checked`, or `not_applicable`, with its evidence and limits. A file's existence or successful compilation alone does not establish content accuracy.

Fix confirmed defects within the authorized scope. If a change needs new requirements or permission, explain what is missing and wait for it. Feedback does not replace authorization for a new model run, external data transfer, or publication.

## After an important delivery

First provide a result the user can inspect. Then offer the following once for that delivery version:

> Does this deliverable meet your needs? You can skip this question.

| Choice | Stored value | Next step |
|---|---|---|
| Meets my needs | `accepted` | Record the response for this version; retain existing verification and permissions |
| Needs a few changes | `adjust` | Apply clear requested changes, or ask one focused question if the change is unclear |
| Does not meet the request | `off_target` | Revisit the goal and identify the mismatch before continuing |

Use chat choices when the host supports them. Otherwise present the three options as text and accept a number or written response; no new interface is required.

If the user already gave explicit feedback about that version, do not ask again. No answer remains `pending`; it is not acceptance. Do not send reminders when the user moves on. Use `skipped` only when the user explicitly skips.

## Turn feedback into appropriate work

| Category | Example | Response |
|---|---|---|
| Defect | A calculation or interpretation is wrong | Check evidence, correct the work, and add a relevant check when useful |
| Requirement mismatch | Wrong file type or page count | Match the current requirements |
| Preference | Shorter text or another example | Apply to this task; do not automatically make it a rule for every course |
| Scope change | New section or different data | Increment requirements revision, invalidate stale readiness, and verify again |

A claim that a fact is wrong still needs evidence. Do not make an answer inaccurate to gain approval. When selected output changes, increment its artifact revision and verify the revised file.

## Bind feedback to what was delivered

Record `delivery_id`, `task_id`, requirements revision/hash, and artifact revision/hash. For a chat answer, hash the delivered text. Build the delivery snapshot from actual output, and clarify an ambiguous response before assigning it to a version.

Earlier feedback remains history after a new delivery. Do not transfer acceptance to the new version. Objective verification, satisfaction, and actual submission are separate records; feedback is not a required assignment field.

Keep real responses in private state. The repository contains only fictional feedback examples. Saved lessons can help a later assistant that reads them, but do not imply model-weight changes or permanent capture of every conversation.

## Measure improvement honestly

Useful starting measures are the first review result, number of revision rounds, and reasons for changes. Separate defects from preferences and scope changes. If reporting satisfaction, include the number of explicit responses and pending deliveries; do not count silence as success.

## Try the contract

The [pending example](../examples/feedback/pending.json) contains no user response. Tests use simulated responses to check the rules:

~~~sh
python -B tools/check_blueprint.py
python -B -m unittest discover -s tests -p test_feedback.py -v
~~~

The checks must allow skipping, prevent feedback from applying to a different delivery, and keep failed verification and execution permissions unchanged after acceptance. See the [data contract](data-contracts.md) for record fields and limits.

# Workspace working instructions - example

This is an instruction template. Adapt it to your needs and save it as `AGENTS.md` in the workspace where you want to use it. Check your assistant's documentation for instruction discovery and scope; placing this template in a folder does not configure every app automatically.

## Start from the task

- Use the user's current request to identify the subject, course, project, or assignment. General questions do not require a folder choice or a saved note.
- Read only the relevant instructions and context. Explicitly open applicable nested instructions when automatic discovery is uncertain.
- Read `current_requirements` before relying on historical notes. Current user instructions take precedence over stored context.
- When a confirmed correction conflicts with metadata, update the current state and record which requirement it supersedes.

## Work with files

- Preserve original source and teaching materials; make working copies for edits and experiments.
- Use the registered interpreter or kernel. Do not infer the project environment from `PATH` or run a whole notebook just to explain a concept.
- Use one primary writer per task. When switching assistants, hand off the scope, inputs, current output, next action, and verification evidence.
- Keep enough internal numerical precision for the calculation; round displayed values according to the task requirements.
- Keep temporary output and dependencies separate from deliverables.
- Follow task-specific permissions for experiments, uploads, publication, and other external actions. A note or status field does not grant permission.

## Verify and record

- Bind verification to both `requirements_revision` and `artifact_revision`.
- Fingerprint `current_requirements` using canonical JSON SHA-256. Reject stale readiness even if someone forgot to increase a revision number.
- Read the JSON evidence and require `passed=true`, matching revisions, the requirements hash, and the artifact hash for every selected file.
- Check the actual files and checksums before using `ready_to_submit`.
- Use meaningful checks appropriate to the work, such as calculation and execution checks for code or content and layout review for reports.
- Set `submitted` only when there is actual user-confirmed submission evidence.
- Record pending work and the selected current artifact so another session can resume from files.
- Do not infer exam coverage, completed lessons, or mastery from the existence of a file.
- Never claim that a runtime, integration, backup, or external action succeeded without observing it.

## Private configuration and publication

- Keep machine-specific paths and credentials in private configuration. Do not put secret values in context files.
- Publish only reviewed public examples and documentation. Keep personal workspace state, real coursework, and source evidence private.
- Shared files provide context across assistants; conversation histories, accounts, tools, and permissions remain separate.

## Optional feedback after important deliverables

- If the workspace owner adopts this loop, define success, verify suitable evidence, correct confirmed issues within scope, and deliver the result with its material limits.
- Offer once per delivered version: **Works as intended**, **Needs some changes**, or **Does not meet the goal**. Allow skipping. Do not ask after casual questions, short explanations, progress messages, or intermediate steps.
- If a chat choice tool is available, use it only after the result is reviewable. Otherwise present the three choices as text. Do not promise installed buttons or background automation.
- Leave unanswered feedback pending. Do not send automatic reminders or infer satisfaction. Record only explicit responses and bind them to the delivery identity, revisions, and hashes.
- Keep objective verification separate. Feedback does not grant execution or upload permission and does not prove submission. Acceptance of an old version does not transfer to changed requirements or artifacts.
- Distinguish defects, unmet requirements, preferences, and scope changes. Recheck the affected work and keep preferences task-scoped unless the user explicitly broadens them.
- Store real feedback privately. Positive feedback does not establish mastery or imply that a model has been retrained.

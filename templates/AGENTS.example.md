# Workspace working instructions — example

This is a template. Rename and adapt it to AGENTS.md only when adopting the design.

## Start from the task
- Resolve the course and assignment from the user's current request.
- Read only the matching course instructions and context, plus assignment context when relevant.
- Read current_requirements before using history. Current user instructions take precedence over stored context.
- When confirmed corrections conflict with metadata, update current state and record which requirement was superseded.

## Work with files
- Preserve instructor originals; edit an explained/lab copy.
- Use the registered interpreter or kernel. Do not infer the environment from PATH.
- Use one primary editor per task; hand off scope, inputs, outputs, and verification when switching tools.
- Calculate with sufficient internal precision; round displayed values according to the assignment.
- Keep temporary output and dependencies out of submission artifacts.

## Verify and record
- Tie verification to both requirements_revision and artifact_revision.
- Fingerprint current_requirements with canonical JSON SHA-256. Reject stale readiness even when a revision bump was forgotten.
- Read JSON evidence and require passed=true, matching revisions, requirements hash and artifact hash for every selected file.
- Check actual files and checksums before ready_to_submit.
- Record meaningful checks appropriate to the work: calculation/run checks for code, layout/content checks for reports.
- Set submitted only after actual user-confirmed submission evidence.
- Record pending work and the current artifact so another session can resume from files.
- Never claim that a runtime, integration, backup, or external action succeeded without observing it.

## Private configuration and publication
- Store machine paths and credentials in private configuration.
- Publish selected public examples and documentation rather than copying the personal workspace into a repository.

## Optional feedback after important deliverables
- When the owner adopts this loop, define success, verify appropriate evidence, fix confirmed issues within scope, and deliver with material limits.
- Offer once per delivered version: "ใช้ได้ตามต้องการ" / "ขอปรับบางจุด" / "ยังไม่ตรงโจทย์". Allow skipping. Do not ask after casual questions, short explanations, progress messages or intermediate steps.
- If a chat choice tool is available, use it only after the result is reviewable; otherwise present the three choices as text. Do not promise installed buttons or background automation.
- No response remains pending; do not prompt again automatically or infer satisfaction. Record only explicit responses and bind them to delivery identity, revisions and hashes.
- Keep objective verification separate. Feedback never grants execution/upload permission or proves submission. Old acceptance does not transfer when the requirements or artifact change.
- Distinguish defects, unmet requirements, preferences and changed scope. Recheck affected work; keep preferences task-scoped unless the user explicitly broadens them.
- Store real feedback privately. Do not add it to public examples or infer mastery/model retraining from a positive response.

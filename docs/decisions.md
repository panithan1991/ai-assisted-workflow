# Engineering decisions

These architectural decision records explain the Blueprint's choices. They describe a practical starting point, not a requirement to use one assistant, folder naming scheme, or hosting service.

## ADR-001: Start with files and a small index

**Decision:** Use JSON for structured state and Markdown for explanations.

**Reason:** Records are readable, easy to back up, usable by different tools, and reviewable as Git diffs.

**Trade-off:** Concurrent writers need coordination. Start with one responsible writer per edit batch; consider a database and transactions when actual collaboration needs justify them.

## ADR-002: Separate current state from history

**Decision:** Keep one current requirements set and retain superseded instructions in history.

**Reason:** This reduces the risk of restoring outdated instructions and keeps the context needed to resume work small.

**Trade-off:** A confirmed correction must update current state and record the change together.

## ADR-003: Bind verification to two revisions

**Decision:** Track `requirements_revision` and `artifact_revision`, together with content hashes.

**Reason:** A reviewed file can become stale when the task changes or its content is edited after review.

**Trade-off:** A little more metadata is needed, but mismatched evidence can be rejected.

## ADR-004: Separate project and AI-tool runtimes

**Decision:** Identify the interpreter or kernel for each project and retain evidence of relevant checks.

**Reason:** An unqualified `python` may use a different environment from the notebook or project. Machine-level GPU information is separate from framework availability in that environment.

**Trade-off:** Several environments require clear references and task-specific dependency management.

## ADR-005: Name a responsible writer

**Decision:** Let the user and coordinating assistant define scope and file ownership for each edit batch.

**Reason:** Clear ownership reduces conflicting edits and helps trace results to their inputs and checks.

**Trade-off:** Not every assistant writes at once. Parallel work is useful when tasks and files can be separated; shared files still require serialization.

## ADR-006: Preserve working paths during adoption

**Decision:** Point the index to existing folders and introduce the proposed layout with new tasks first.

**Reason:** Notebooks, multipage applications, document sources, and scripts may depend on existing paths.

**Trade-off:** Old and new layouts may coexist. A later migration needs an explicit path mapping and verification.

## ADR-007: Separate the public Blueprint from private work

**Decision:** Publish selected documentation, code, and fictional examples in a dedicated repository.

**Reason:** Other people can adapt the workflow without receiving private coursework, reports, credentials, or service configuration.

**Trade-off:** Public examples need maintenance as the design evolves. Machine-specific details remain in private configuration.

## ADR-008: Do not require an orchestration service

**Decision:** Start with documented steps and a reference checker.

**Reason:** The first problems to solve are context, versions, evidence, and runtime selection. Adding more agents does not by itself solve those problems.

**Trade-off:** Some steps remain manual. Automate a repeatable step after its inputs, criteria, and benefit are clear, while retaining the same data contracts.

## ADR-009: Use MIT for the Blueprint

**Decision:** Apply the [MIT License](../LICENSE) to material the project has the right to license.

**Reason:** It permits reuse, modification, and redistribution, including commercial use, under its notice requirements.

**Trade-off:** MIT does not require downstream changes to be published or contributed back. Third-party material retains its own rights, and a public license does not authorize publishing a private workspace.

## ADR-010: Separate shared knowledge from operational state

**Decision:** Optionally connect projects through sourced Markdown notes, with a shared portal and domain-specific entry points.

**Reason:** Concepts and lessons can be reused across work, study, and personal interests while each source project retains ownership of current requirements and status.

**Trade-off:** Shared notes need one coordinated writer or a single agreed claim registry. Existing indexes and source paths must be preserved. The [shared knowledge guide](shared-knowledge.md) documents the pattern; no file-locking or synchronization service is bundled.

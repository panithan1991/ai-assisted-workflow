# Workflows

Start with the [runnable walkthrough](walkthrough.md) to see state changes and expected rejections using fictional files.

## Daily learning

~~~mermaid
sequenceDiagram
    participant U as Learner
    participant A as Assistant
    participant S as Context and sources
    participant R as Runtime
    U->>A: Course, source, and question
    A->>S: Read current lesson and relevant source
    A-->>U: Explain at the learner's current level
    opt An experiment is needed and authorized
        A->>S: Create a working copy
        A->>R: Run in the selected environment
        R-->>A: Result or error
        A-->>U: Explain the result and verified limits
    end
    A->>S: Save important context when appropriate
~~~

A request such as "Continue the tensor lesson in this notebook" is enough when course context is already known. A conceptual explanation does not require installing packages, starting services, or executing the entire notebook.

Keep original material, working copies, learning notes, and run outputs distinct. Follow the lesson progression the learner confirms; seeing a topic in a file does not establish that it has been completed or mastered.

## Assignments and reports

~~~mermaid
stateDiagram-v2
    [*] --> inbox
    inbox --> in_progress: Current task confirmed
    in_progress --> in_review: Draft available
    in_review --> in_progress: Revision needed
    in_review --> ready_to_submit: Current files and evidence pass
    ready_to_submit --> in_progress: Requirements or output change
    ready_to_submit --> submitted: Actual submission evidence
    submitted --> in_progress: Revision or resubmission needed
    submitted --> archived: Work closed
~~~

1. **Capture the task.** Preserve originals, source references, and confirmed corrections.
2. **Record current requirements.** Include the revision and task-specific criteria, such as page count, numerical precision, and calculation scope.
3. **Do the work.** Create editable code or documents in the working area and record the runtime and inputs.
4. **Verify.** Check relevant calculations, execution results, and document layout. Record JSON evidence bound to current requirements, revisions, and selected file hashes.
5. **Select output.** Identify deliverable files and their checksums; retain the editable sources.
6. **Deliver and invite feedback.** State what was checked and any material limits. For important work, offer optional feedback once for this version. Feedback does not establish technical validity; see the [feedback loop](feedback-loop.md).
7. **Record actual submission.** Use `submitted` only after user confirmation with evidence, such as a receipt. A PDF or an acceptance response is insufficient.

## When requirements change

For example, a reviewed report may gain a required Limitations section:

- Retain the previous instruction in history and increment `requirements_revision`.
- Store the new requirement in `current_requirements`.
- Record which earlier instruction it supersedes.
- Do not use the earlier review as evidence for the new requirements.
- Even if somebody misses the revision increment, a changed `requirements_sha256` reveals the mismatch.
- Return stale `ready_to_submit` work to `in_progress`, revise it, and verify again.

Update current state and history together rather than asking an assistant to infer the newest instruction from a long conversation.

The checker reports inconsistencies without rewriting state. The user or responsible tool must make the state change and perform the revision and review.

## Resume a task

Read only what the request needs:

1. The workspace index to locate the task.
2. Applicable instructions and course or project context.
3. The assignment record for a deliverable.
4. Current requirements, selected artifacts, verification, and remaining actions.
5. Original sources needed to confirm a fact.

If records conflict, resolve them using the current user instruction and confirmed source evidence before proceeding. Historical chat should not replace the authoritative current record.

## Select a runtime

| Task | Suggested starting point |
|---|---|
| Explain a concept | Conversation and the relevant source section |
| Follow a hosted classroom notebook | A working copy in the selected cloud notebook |
| Local experiment | Explicit environment and a minimal relevant check |
| Database lab | Authorized local container or hosted database, using sample data |
| Report with formulas and figures | Editable source, LaTeX/PDF generation, and page inspection |
| Search several documents | A selected retrieval collection with links back to originals |
| Research experiments | A separate project with an agreed plan and recorded results |

Choosing a route does not establish that its environment is ready. Verify the runtime needed for that task.

## Hand off between AI tools

Provide the incoming tool with scope, authoritative context, input paths, output location, and acceptance criteria. Name a responsible writer for each edit batch. Before another tool writes the same files, record changes, actual checks, and remaining work, then hand over ownership.

Applications retain their own authentication, permissions, and conversation history. File-based continuity works only when the relevant files have actually been saved and the receiving tool can read them.

## Connect reusable knowledge

A [shared knowledge vault](shared-knowledge.md) can hold sourced explanations and lessons that are useful across tasks. Keep current requirements and submission status in the owning project, and use notes to link concepts and source material.

General questions do not require a new note, course selection, or feedback form.

## Publish a reusable subset

1. Use a dedicated repository for the Blueprint and examples.
2. Select material that may be shared; do not copy an entire private workspace.
3. Check example JSON, local documentation links, and workflow tests.
4. Review rights and visibility. This Blueprint uses the [MIT License](../LICENSE).
5. Review the exact file set, then publish only within the owner's instructions.

# Adoption plan

Adopt the workflow one task at a time. This guide describes steps you can take; it does not install environments, move files, or connect applications.

The repository provides documentation, fictional examples, a reference checker, tests, and a temporary-file demonstration. Your runtime, permissions, source material, and application access still need to be configured and verified.

## Stage 1: Find the current task

- Add a short root `AGENTS.md` using the [instruction template](../templates/AGENTS.example.md).
- Create an index that points to existing course and project folders.
- Keep current lesson or project context separate from long schedules and logs.
- Choose one authoritative record for each assignment's current requirements and revisions.
- Identify the files selected for the next delivery.

**Success criterion:** Given a course and task ID, you can find the current requirements, original sources, and selected files without reconstructing the entire chat history.

The identifiers in [examples](../examples/README.md) are illustrative. Replace them with your own course or project names; a particular naming convention is not required.

## Stage 2: Reproduce one small experiment

- Preserve the instructor's original notebook or source file.
- Create a working copy and choose an explicit interpreter or notebook kernel.
- Record the runtime, dependencies, inputs, and outputs.
- Run only the small checks needed for the experiment.
- For a GPU task, test the framework in that environment rather than relying on driver information.

For example, a first PyTorch lab might check an import, tensor creation, matrix multiplication, and automatic differentiation. Test `torch.cuda.is_available()` when CUDA availability matters. The [architecture guide](architecture.md) explains the environment boundary.

**Success criterion:** Another person can reproduce the experiment using the recorded runtime and inputs.

## Stage 3: Complete one deliverable

- Separate original material, editable source, working files, and selected output.
- Record confirmed corrections in current requirements; preserve superseded instructions in history.
- Check calculations, execution results, or document layout as appropriate.
- Bind verification to the requirements revision, artifact revision, and hashes.
- Change a requirement after review and confirm that the old verification no longer establishes readiness.

Start with the [runnable walkthrough](walkthrough.md), then apply the contract to one real assignment or report.

**Success criterion:** `ready_to_submit` identifies the reviewed current files and cannot rely on evidence from an older version.

## Stage 4: Expand carefully

- Register more courses and projects while retaining their working paths.
- Reference external projects without copying their large environments into the workspace.
- Keep computer maintenance separate from coursework.
- Back up sources, metadata, dependency specifications, and selected outputs. Treat reproducible caches and installed dependencies separately under your backup policy.
- Add another AI tool when it has a clear role, and name the responsible writer for each edit batch.
- Optionally add a [shared knowledge vault](shared-knowledge.md) for reusable notes across work, study, and general interests.

**Success criterion:** Adding a course or tool does not change another course's rules or overwrite its current state.

## Stage 5: Share a reusable subset

- Select documentation, templates, and fictional examples you have permission to distribute.
- Review the exact publication file list for credentials, personal paths, and private work.
- Run the checker, tests, and walkthrough from the repository root.
- Publish within the owner's instructions and chosen visibility.
- Use CI to repeat the checks on pushes and pull requests.

This Blueprint uses the [MIT License](../LICENSE). Review third-party rights separately before adding material from other people.

## Measure the result

Record a baseline before claiming an improvement. Useful measures include:

- Time needed to find the selected deliverable.
- Time needed to resume a task in a new chat.
- Runs started with the wrong interpreter or kernel.
- Edits made against stale requirements or the wrong file version.
- Time from receiving source material to a successful first example.

Separate defects from preference changes and new requirements. Report observed results and sample sizes rather than inventing a percentage improvement.

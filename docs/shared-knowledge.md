# Shared knowledge across projects

A shared note collection can connect work, study, and general interests while each project retains its own files and rules. This is an optional adoption pattern. The repository does not install a note-taking app, connect accounts, or provide a note synchronization service.

Obsidian is one possible reader and editor: its vault is a local folder of Markdown files that other editors can also use. See its [data storage documentation](https://obsidian.md/help/data-storage). A regular text editor or another compatible note application can serve the same role.

## Separate the three responsibilities

| Layer | Responsibility |
|---|---|
| Project workspaces | Original sources, code, data, current requirements, selected outputs, and verified status |
| Shared knowledge collection | Sourced explanations, comparisons, reusable lessons, and links back to the owning project |
| Reading and editing tools | Display, search, edit, and connect the saved notes within their granted access |

A note about an assignment does not replace its requirements record. A note saying a report was sent does not establish submission without the owning project's evidence.

## Start with a small collection

The following is a proposed layout, not a generated directory tree:

~~~text
knowledge-vault/
|-- AGENTS.md
|-- wiki/
|   |-- home.md                 # New shared portal
|   |-- index.md                # Existing work index, if one already exists
|   |-- work/
|   |   `-- index.md
|   |-- study/
|   |   `-- index.md
|   `-- general/
|       `-- index.md
|-- raw/                        # Existing source material, preserved
`-- Clippings/                  # Existing captured material, preserved
~~~

Use domain names appropriate to your work. A small initial collection is easier to review than a bulk copy of every chat, notebook, environment, or dataset.

## Route each question to its owner

Shared instructions should identify which project owns each domain:

| Domain | Read before substantive work | Authoritative state |
|---|---|---|
| Work | Work-project instructions and relevant evidence | That project's current state and artifact register |
| Study | Applicable course/project instructions and teaching sources | Selected task record in the learning workspace |
| General interests | Relevant personal-project context when needed | That project's records or the current user request |

For mixed questions, preserve the ownership of each fact. Official document rules should not automatically govern homework; course assumptions should not govern an administrative task.

Read only the relevant context. A casual question does not need every project's instructions, every note, or a new saved page.

## Preserve existing indexes and paths

Before extending an existing vault:

1. Identify its original indexes, their owners, and any scripts that regenerate them.
2. Preserve the old index and note paths.
3. Add a separate shared portal, such as `wiki/home.md`, and domain entry pages that link back to existing indexes.
4. Keep original PDFs, code, and datasets in their current projects; link to them instead of copying whole source trees.
5. Verify new links and compare the protected original files with the pre-change snapshot.

If a legacy script rewrites `wiki/index.md`, adding the new portal to that file alone is not durable. A separate portal avoids repurposing the original index and can survive that existing workflow.

Application settings, themes, layout files, and plugins have a different role from knowledge records. Do not overwrite them merely to add domain navigation.

## Use portable note conventions

For new notes, record a title, domain, source workspace, source references, and update date. Explain the concept, show a useful example, and link to related notes. Distinguish original material, student notes, historical information, and inference.

These are optional note conventions, not fields currently validated by the assignment checker. Use standard relative Markdown links between notes where possible. Obsidian supports both its own link syntax and [standard Markdown links](https://obsidian.md/help/links); standard links are easier to reuse in other Markdown readers. External local-file links may need machine-specific configuration and should not be copied into public examples.

Do not infer mastery, current exam scope, approval, or completed work from the existence of a note.

## Coordinate all shared writers

Every assistant that writes the same knowledge collection needs the same ownership agreement. Choose one responsible writer at a time, or one agreed claim registry for every shared note and common index.

If adopting a claim tool, agree on its scope, owner identification, freshness checks, and release procedure. A tool in one project must not independently claim the same shared file in a different registry. For a task spanning several workspaces, obtain the necessary ownership before changing either side.

Claims are cooperative coordination, not operating-system permissions or guaranteed protection against uncooperative writers. If files change unexpectedly, reread them and reconcile the changes rather than replacing a stale snapshot.

**No claim CLI or locking service is bundled in this repository.** Until a separately reviewed tool is adopted, serialize shared edits and hand off explicitly. The reference checker validates the Blueprint's data contracts; it does not reserve files.

## Keep continuity explicit

When important reusable knowledge is ready:

1. Check it against the relevant original sources.
2. Save the note and update the appropriate domain index.
3. Update the owning project's current state if the task itself changed.
4. Leave a short handoff pointing to the current record and actual verification.

An assistant can use saved knowledge only when it has access and actually reads it. Shared files do not automatically share chat histories, accounts, credentials, permissions, or model memory. This pattern does not authorize external data transfer, publication, plugins, background synchronization, training, or other actions beyond the user's task.

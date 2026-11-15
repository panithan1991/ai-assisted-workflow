# Architecture

## Scope and outcomes

The workflow supports a repeatable cycle: learn, explain, experiment, produce a deliverable, verify it, and return to it later. It can span several courses and AI tools without requiring a central database or background service.

The design aims to make these outcomes inspectable:

- A task ID leads to its current requirements, original sources, runtime information, and selected output.
- A confirmed requirement change makes previous verification stale.
- Machine-level GPU capability is separate from framework availability in a particular environment.
- A reviewed deliverable is distinguishable from an actually submitted deliverable.
- A reusable public Blueprint can be shared without publishing a private workspace.

## System context

~~~mermaid
flowchart LR
    T["Instructor or team"] -->|"Requirements, sources, corrections"| W["Personal workspace"]
    U["User"] -->|"Task and goal"| W
    W -->|"Question or authorized task"| AI["AI assistant"]
    AI -->|"Explanation, code, draft"| W
    W -->|"Experiment"| R["Colab / Python / Docker"]
    R -->|"Results and evidence"| W
    W -->|"Reviewed deliverable"| U
    U -->|"Actual submission"| S["Submission channel"]
    W -->|"Reviewed shareable subset"| G["GitHub"]
~~~

These arrows describe a workflow, not an installed integration. They do not imply shared accounts, automatic file access, or synchronized chat history.

## Components and responsibilities

| Component | Responsibility | Input | Output |
|---|---|---|---|
| Workspace index | Locate a course, project, or task | Stable IDs | Context paths and entry points |
| Context loader | Read only relevant information | Index and current request | A focused context set |
| Task controller | Organize work and track progress | Context and requirements | Steps, state, and remaining actions |
| Source registry | Identify the origin and version of material | Files or URLs, hashes when available | Traceable source references |
| Execution router | Select where a task runs | Task type and environment registry | Chosen local, cloud, or container runtime |
| AI adapter | Use a suitable tool within its access and task scope | Request and permitted files | Explanation, code, or draft |
| Verification | Compare work with current criteria | Deliverable and requirements | Pass/fail evidence and limitations |
| Artifact registry | Identify selected output | Files, revisions, hashes, and verification | Manifest of the selected version |
| History and backup | Retain important changes and earlier versions | Change events | An audit trail and recoverable copies |

The context loader, task controller, and execution router are initially documented responsibilities carried out by the user and assistant. This repository does not provide a daemon or an agent orchestration service.

## Load context by task

~~~mermaid
flowchart TD
    A["Request: course and assignment"] --> B["Workspace instructions"]
    B --> C["Relevant workspace index entry"]
    C --> D["Course or project instructions and context"]
    D --> E["Authoritative task record"]
    E --> F["Current requirements"]
    F --> G["Required sources, code, and artifact records"]
    E -. "Only when needed" .-> H["Historical context"]
~~~

Keep stable working rules in `AGENTS.md`. Store changing requirements, schedules, long logs, and source content in separate files.

When adopting an existing workspace, current records can live in a private `_workspace/state/` directory, with the index pointing to them. Legacy scripts may continue to write older metadata files; those files must not silently regain authority over the selected current record. The short paths in this repository's fictional examples illustrate the same principle: one authoritative record per task.

When working from a workspace root, explicitly direct the assistant to read the applicable course or project instructions. Codex discovers project instructions along the path from the project root to the current working directory; opening the root does not mean every descendant `AGENTS.md` is loaded. See [OpenAI's instruction guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md). Other clients may discover instructions differently, so check their documentation and access before depending on automatic loading.

## An adaptable folder layout

~~~text
workspace/
|-- AGENTS.md                    # Shared rules and context routing
|-- _workspace/
|   |-- index.json               # Paths, not duplicate requirements
|   |-- environments.json        # Runtime references and verification
|   |-- state/                  # Current records for an existing workspace
|   |   |-- courses/
|   |   `-- assignments/
|   `-- templates/
|-- Inbox/                      # Material not yet assigned to a task
|-- course-a/                   # Existing names and paths may be retained
|-- course-b/
|   |-- AGENTS.md
|   |-- course-context.json
|   |-- Lectures/               # Original teaching material
|   |-- Notes/
|   |-- Projects/
|   |-- Labs/
|   |   `-- first-lab/
|   |       |-- notebooks/
|   |       |-- src/
|   |       |-- outputs/
|   |       `-- requirements.txt
|   `-- Assignments/
|       `-- example-assignment/
|           |-- assignment-context.json
|           |-- original/
|           |-- src/
|           |-- working/
|           |-- submission/
|           `-- archive/
`-- Tools/System/               # Maintenance utilities, separate from lessons
~~~

This is a proposed layout, not a directory tree created by the checker. Start with new tasks and point the index to existing projects. Before a later move, prepare an old-to-new path mapping and verify affected links and files.

## Choose tools by role

| Tool category | Example use | What must be established |
|---|---|---|
| File-aware AI assistant | Explain material, edit code, draft, review | Instructions, file access, scope, and responsible writer |
| Hosted notebook | Follow a classroom example or use cloud compute | Selected notebook, runtime, and service limits |
| Local Python environment | Reproduce experiments on the user's machine | Explicit interpreter or kernel and dependencies |
| Container runtime | Isolate a database or supporting service | Configuration, data location, and ports |
| Local model service | Inference with a chosen installed model | Availability, resources, and data handling |
| Document retrieval tool | Search a selected collection | Included documents and links to originals |
| Research agent | A separately scoped research project | Experiment plan, criteria, permissions, and results |
| LaTeX and PDF tools | Produce and inspect formula-heavy documents | Editable source, compilation setup, and rendered-page review |

The Blueprint does not require every tool to run at once, configure providers, or change model selections. Tools such as Codex, Antigravity, Colab, Docker, Ollama, and other assistants can fill a role when the user chooses and verifies them; no adapter installation is bundled here.

## Environment contract

For each environment, record:

- Its ID, type, and activation method.
- The verified interpreter path or notebook kernel, kept in private configuration when machine-specific.
- The task's dependency specification or lockfile.
- The date and evidence of a successful minimal check.
- Framework-level CUDA availability when relevant, separate from the machine's GPU and driver.

Use the recorded interpreter or kernel for local execution. A command called `python` on `PATH` may belong to an AI tool rather than the project.

Driver information does not establish that a particular PyTorch installation can use CUDA. NVIDIA's [CUDA UMD version documentation](https://docs.nvidia.com/deploy/nvidia-smi/index.html#cuda-umd-version) describes driver capability; the framework still needs testing in its selected environment. A cloud notebook's GPU belongs to that cloud runtime, not the user's local machine.

## Data ownership

| Information | Authoritative location |
|---|---|
| Original teaching or work material | Original source files and references |
| Current requirements | `current_requirements` in the selected task record |
| Task-specific writing and precision rules | Task record; shared defaults remain in instructions |
| Current lesson or course context | Course record |
| Selected output | Artifact paths, revisions, and hashes in the task record |
| Earlier requirements and versions | History or archive |
| Credentials and real machine paths | Private local configuration |
| Actual submission | User-confirmed submission evidence |

A [shared knowledge vault](shared-knowledge.md) can connect reusable notes across work, study, and general interests. It remains a layer of sourced explanations and links, not another task-status database.

## Recover and resume

- **Unavailable runtime:** Record what failed and use an authorized alternative if one exists. Avoid broad changes to unrelated environments.
- **Changed requirement:** Increment its revision, invalidate stale readiness, revise the work, and verify again.
- **Several files named final:** Use the selected artifact manifest and hashes to identify the intended version.
- **New chat:** Read the index and focused current context rather than every historical log.
- **Another AI tool takes over:** Hand off the scope, selected files, actual checks, and remaining work before it edits the same files.
- **Backup:** Preserve sources, metadata, dependency specifications, and selected outputs. Apply a separate policy to reproducible caches and installed dependencies.

The [data contracts](data-contracts.md) define these state checks; the [workflow guide](workflows.md) shows how to use them.

# Example workspace

All data in this folder is fictional. It illustrates file organization and workflow contracts, not a real learner's progress, submission history, or verified runtime. The course identifiers are examples and can be replaced with your own.

| File or folder | Purpose |
|---|---|
| [workspace.json](workspace.json) | Routes three example courses and a project to their own context files |
| [environments.json](environments.json) | Lists runtime choices whose availability has not been confirmed |
| `courses/*/course-context.json` | Records example course context and assignment locations |
| [Assignment context](courses/DADS6003/Assignments/NN_homework/assignment-context.json) | Shows a task whose requirements were revised to three derivatives |
| [Requirement history](courses/DADS6003/Assignments/NN_homework/history.json) | Records the confirmed requirement changes |
| [Transaction project](projects/transaction-demo/README.md) | Registers an existing project folder, its instructions, context, and source references without executing it |
| [Walkthrough assignment](walkthrough/assignment.json) | Supplies the fictional report brief used by the [walkthrough](../docs/walkthrough.md) |
| [Pending feedback](feedback/pending.json) | Shows unanswered feedback bound to a delivered version, separate from verification |

The assignment examples use `in_progress`, an empty `artifacts` list, and `verification.passed=false`. These values deliberately avoid claiming that a deliverable is ready or that a runtime has passed verification.

The transaction project is waiting for the user to choose an approach. It contains no dataset, model trainer, service credentials, or experiment results.

The runnable demo creates answer files and synthetic evidence in its own temporary directory. It removes those temporary files when it finishes and does not read or change real coursework. Start with the [repository quickstart](../README.md#try-the-examples).

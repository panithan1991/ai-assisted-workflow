# Transaction demo

This fictional example shows how to register a project that already has its own folder. It contains no real transaction data, model, service account, or experiment results.

Start with the [project context](project-context.json) and [working instructions](AGENTS.md). The [fictional source references](sources.json) demonstrate how to record provenance; they are not a dataset to download.

The workspace index points to this folder without maintaining a second copy of the project's current requirements. The checker reads its metadata and verifies local paths. It does not import project code or run a model.

The project remains in `awaiting_user_round_selection`. Any future experiment would require an explanation of the options and the user's choice for that run. No remote upload is authorized by this example.

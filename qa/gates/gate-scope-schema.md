# Gate Scope Schema v1

Gate scope definition files are JSON documents with the following fields:

- `schema_version`: integer, currently `1`;
- `gate`: certificate key, such as `canon`;
- `scope`: validator scope passed to `validate_project.py`;
- `prerequisites`: already locked gate keys required before preparation;
- `declared_frozen_items`: ordered list of every item ID in `items`;
- `items`: ordered frozen inputs, each containing a stable `id`, repository-relative `path`, and `mode`.

`prepare_gate` hashes every frozen input into `qa/gates/input-manifests/<gate>.json`. A lock requires the same manifest hash in two review documents, distinct reviewer IDs, `status = "PASS"`, and a clean strict validation. Changing any frozen input after preparation invalidates the review set.

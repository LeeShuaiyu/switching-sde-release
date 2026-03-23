# Role Card: Evidence Mapper

## Mission

Create a claim-to-evidence map so later drafts can remain grounded in code and results.

## Inputs

- `artifacts/project_dossier.md`
- repository evidence

## Outputs

- `artifacts/evidence_map.yaml`

## Expected mapping fields

- `claim_id`
- `statement`
- `status` such as `supported`, `partially_supported`, or `unsupported`
- `source_type`
- `source_path`
- `locator`
- `notes`
- `figure_or_table_id` when a claim is best supported by a named visual asset

## Quality standard

- Every strong claim required by the report should have an entry.
- Unsupported claims must remain visible rather than silently dropped.

## Must not do

- Use vague references such as "some log" or "the training script" without a path or locator.

# Runs Directory

Each workflow execution should create a subdirectory here.

A run directory contains:

- `run_state.yaml`: machine-readable stage status
- `events.jsonl`: append-only event log
- `briefs/`: per-stage briefs that can be handed to Codex subagents
- `validation_report.md`: latest validation report for the run

Recommended usage:

1. Initialize a run with `tools/run_workflow.py init`
2. Claim and complete stages through the runtime CLI
3. Regenerate stage briefs as needed with `tools/run_workflow.py brief`
4. Validate the run with `tools/validate_workflow.py`

Runs are intended to be auditable snapshots, not scratch space.

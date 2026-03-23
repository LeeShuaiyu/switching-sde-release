# Runtime Layer

This directory contains the machine-readable runtime contract that turns the writing pipeline from a prompt protocol into a Codex-subagent-ready workflow.

Files in this directory:

- `stages.yaml`: machine-readable stage registry
- `codex_subagent_contract.md`: execution contract for Codex subagents

The runtime is intentionally simple:

1. `stages.yaml` defines ordered stages, owners, dependencies, read sets, write scope, and required outputs.
2. `tools/run_workflow.py` creates and updates run state under `writing-pipeline/runs/`.
3. `tools/validate_workflow.py` checks whether a run satisfies the publishable workflow contract.

The runtime does not try to author the manuscript automatically. Instead, it provides the missing orchestration layer so Codex or Codex subagents can claim bounded work, leave an auditable run log, and stop only when the configured gates pass.

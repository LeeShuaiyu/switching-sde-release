# Writing Pipeline

This folder is a publishable writing workflow for Codex and Codex subagents.

It combines four layers:

1. Protocol documents in `START_HERE.md`, `workflow.md`, and `roles/`
2. Machine-readable runtime metadata in `runtime/stages.yaml`
3. Executable orchestration tools in `tools/`
4. Auditable run directories in `runs/`

## What makes it publishable

- Stage order is defined both in prose and in a machine-readable manifest.
- Runs leave state, events, stage briefs, and validation reports on disk.
- Deliverables are checked for bilingual completeness, figure-manifest coverage, and rendered HTML outputs.
- The runtime is designed for bounded Codex subagent work rather than free-form roleplay.

## Core commands

Initialize a run:

```bash
python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml init --run-id demo
```

Sync existing outputs into the run state:

```bash
python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml sync --run-id demo
```

Inspect status and generate briefs:

```bash
python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml status --run-id demo
python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml brief --run-id demo --stage stage_5_report_drafting
```

Validate the run:

```bash
python3 writing-pipeline/tools/validate_workflow.py --config writing-pipeline/run_config.yaml --run-id demo
```

Render HTML outputs:

```bash
python3 writing-pipeline/tools/render_outputs.py --config writing-pipeline/run_config.yaml
```

## Directory guide

- `runtime/`: machine-readable workflow contract
- `tools/`: orchestration, validation, and rendering scripts
- `runs/`: per-run state and validation records
- `artifacts/`: manuscript-planning outputs
- `outputs/`: final markdown and rendered deliverables

## Intended operating model

The orchestrator initializes a run, claims stages, and hands stage briefs to Codex subagents. Each subagent owns only the stage write scope. The orchestrator then validates the run before calling the workflow publishable.

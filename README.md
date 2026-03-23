# switching-sde-release

A publishable release repository for switching stochastic differential equation experiments.

This repository has two complementary roles:

1. A reproducible release layer over legacy experiment artifacts from `PENN`
2. A Codex-subagent-ready writing workflow for producing bilingual, figure-integrated reports and paper drafts

## What Is In This Repository

### 1. Release and compatibility layer

The Python package under `src/` exposes the `switching-sde` CLI for:

- indexing legacy artifacts
- linking them into this repository
- running evaluation in `live`, `frozen`, or `auto` mode
- rebuilding benchmark tables and figures
- generating release reports and bundles

The design goal is to keep the legacy experiment repository untouched while making the final artifacts reproducible and publishable from a cleaner repository.

### 2. Writing pipeline

The `writing-pipeline/` folder is a structured authoring workflow for turning the codebase and its checked-in results into:

- a self-contained technical report
- a paper-style manuscript fragment
- matched English and Chinese versions
- rendered HTML outputs with embedded figures
- an auditable figure manifest
- a machine-readable runtime that supports Codex subagent stage briefs, run-state tracking, and validation

## Repository Layout

```text
src/                    Python package and CLI implementation
scripts/                release and preflight helpers
tests/                  unit and integration tests
assets/                 manifests and linked artifact metadata
reports/                generated benchmark/report outputs from the release layer
writing-pipeline/       bilingual writing workflow and runtime
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .
```

If editable install is unavailable in your environment:

```bash
pip install .
```

## Release CLI Usage

Set the legacy artifact root first. If `--legacy-root` is omitted, the CLI tries `LEGACY_PENN_ROOT` and then `../PENN`.

```bash
export LEGACY_PENN_ROOT=/path/to/PENN
```

Index and link legacy artifacts:

```bash
switching-sde artifacts index --legacy-root "$LEGACY_PENN_ROOT"
switching-sde artifacts link --legacy-root "$LEGACY_PENN_ROOT"
```

Run benchmark/report generation:

```bash
switching-sde benchmark --suite paper_full --mode frozen
switching-sde report --suite paper_full
```

Main commands:

- `switching-sde artifacts index --legacy-root <path>`
- `switching-sde artifacts link --legacy-root <path>`
- `switching-sde eval --experiment <name> --mode live|frozen|auto`
- `switching-sde viz --experiment <name> --mode live|frozen|auto`
- `switching-sde benchmark --suite paper_full|p5|p6 --mode live|frozen|auto`
- `switching-sde report --suite paper_full|p5|p6`

Execution policy:

- `live`: run compatible evaluation or visualization against available checkpoints and datasets
- `frozen`: regenerate outputs strictly from existing tracked results
- `auto`: try `live`, then fall back to `frozen`

## Writing Pipeline Usage

The writing pipeline lives in [`writing-pipeline/README.md`](writing-pipeline/README.md) and [`writing-pipeline/START_HERE.md`](writing-pipeline/START_HERE.md).

### Render current outputs

```bash
python3 writing-pipeline/tools/render_outputs.py --config writing-pipeline/run_config.yaml
```

This refreshes:

- `writing-pipeline/outputs/report.html`
- `writing-pipeline/outputs/report.zh.html`
- `writing-pipeline/outputs/paper.html`
- `writing-pipeline/outputs/paper.zh.html`
- `writing-pipeline/outputs/figure_manifest.md`

### Initialize an auditable workflow run

```bash
python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml init --run-id demo
```

Inspect runnable stages and generate a stage brief for a Codex subagent:

```bash
python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml next --run-id demo
python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml brief --run-id demo --stage stage_0_repository_intake
```

Sync the run state against outputs that already exist on disk:

```bash
python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml sync --run-id demo
```

Validate the run:

```bash
python3 writing-pipeline/tools/validate_workflow.py --config writing-pipeline/run_config.yaml --run-id demo
```

The runtime leaves audit files under `writing-pipeline/runs/<run_id>/`:

- `run_state.yaml`
- `events.jsonl`
- `briefs/<stage>.md`
- `validation_report.md`

## Example Outputs

Current final deliverables are stored under `writing-pipeline/outputs/`:

- [`writing-pipeline/outputs/report.md`](writing-pipeline/outputs/report.md)
- [`writing-pipeline/outputs/report.zh.md`](writing-pipeline/outputs/report.zh.md)
- [`writing-pipeline/outputs/paper_sections.md`](writing-pipeline/outputs/paper_sections.md)
- [`writing-pipeline/outputs/paper_sections.zh.md`](writing-pipeline/outputs/paper_sections.zh.md)
- [`writing-pipeline/outputs/report.html`](writing-pipeline/outputs/report.html)
- [`writing-pipeline/outputs/report.zh.html`](writing-pipeline/outputs/report.zh.html)
- [`writing-pipeline/outputs/paper.html`](writing-pipeline/outputs/paper.html)
- [`writing-pipeline/outputs/paper.zh.html`](writing-pipeline/outputs/paper.zh.html)
- [`writing-pipeline/outputs/figure_manifest.md`](writing-pipeline/outputs/figure_manifest.md)

## Validation

Package and CLI sanity:

```bash
PYTHONPATH=src python -m switching_sde.cli.main --help
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

Writing workflow validation:

```bash
python3 writing-pipeline/tools/validate_workflow.py --config writing-pipeline/run_config.yaml --run-id demo
```

## Release Preparation

Before tagging a release, run preflight:

```bash
export LEGACY_PENN_ROOT=/path/to/PENN
python scripts/release_preflight.py --legacy-root "$LEGACY_PENN_ROOT"
```

This generates:

- `reports/release/preflight_summary.json`
- `reports/release/preflight_summary.md`
- `dist/switching_sde_release_lite.tar.gz`
- `dist/switching_sde_release_full.tar.gz`

Use `RELEASE_CHECKLIST.md` as the final go/no-go gate.

## License

MIT. See `LICENSE`.

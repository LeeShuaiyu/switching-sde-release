# Release Checklist

This checklist is for publishing `switching-sde-release` as a reproducible package.

## 1) Scope Freeze

- Confirm release version (e.g., `v0.1.0`).
- Freeze experiment scope: `paper_full`, `p5`, `p6`.
- Confirm legacy source path is fixed and readable.
- Confirm no retraining is required for this release.

## 2) Environment Readiness

- Python version is `>=3.9`.
- `pip`, `setuptools`, `wheel` are up-to-date.
- Legacy repo is available (set `LEGACY_PENN_ROOT`).
- GPU is optional for frozen mode; live mode requires legacy runtime dependencies.

## 3) Mandatory Preflight

Run from repository root:

```bash
python scripts/release_preflight.py --legacy-root "$LEGACY_PENN_ROOT"
```

Expected result:

- `reports/release/preflight_summary.json` has `"status": "passed"`.
- `reports/release/preflight_summary.md` exists and all steps are `PASS`.

## 4) Artifact Integrity

- `assets/manifests/artifacts.lock.json` exists and is updated.
- `assets/manifests/datasets.lock.json` exists and is updated.
- `reports/paper/benchmark_summary.json` exists.
- `reports/paper/paper_full_report.md` exists.
- `dist/switching_sde_release_lite.tar.gz` exists.
- `dist/switching_sde_release_full.tar.gz` exists.

## 5) Functional Acceptance

- `switching-sde --help` works.
- Frozen benchmark runs:

```bash
switching-sde benchmark --suite paper_full --mode frozen --legacy-root "$LEGACY_PENN_ROOT"
```

- Auto evaluation runs:

```bash
switching-sde eval --experiment id_nonlinear --mode auto --legacy-root "$LEGACY_PENN_ROOT"
```

- Auto visualization runs:

```bash
switching-sde viz --experiment id_nonlinear --mode auto --legacy-root "$LEGACY_PENN_ROOT"
```

## 6) Documentation and Packaging

- `README.md` has install/quickstart/validation steps.
- `LICENSE` is present.
- `pyproject.toml` and `setup.py` are present.
- CI workflow exists at `.github/workflows/ci.yml`.

## 7) Release Metadata

- Tag format: `vMAJOR.MINOR.PATCH`.
- Record release date.
- Record commit SHA.
- Record preflight report paths.
- Record known limitations (if any).

## 8) Final Go/No-Go

Release is `GO` only if:

- Preflight status is `passed`.
- No failing tests.
- No missing required artifacts.
- Frozen pipeline is reproducible on target machine.

Otherwise `NO-GO` and fix blockers before tagging.

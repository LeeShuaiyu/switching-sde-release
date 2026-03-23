#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from workflow_runtime import (
    collect_required_output_paths,
    document_jobs,
    extract_image_targets,
    extract_markdown_math,
    extract_numeric_tokens,
    load_config,
    load_run_state,
    load_stage_manifest,
    repo_root_from_config,
    runtime_config,
    stage_index,
    save_run_state,
    translation_pairs,
    utc_now,
    validation_report_path,
)


@dataclass
class Issue:
    severity: str
    check: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a writing-pipeline workflow run.")
    parser.add_argument("--config", required=True, help="Path to writing-pipeline run_config.yaml")
    parser.add_argument("--run-id", required=True, help="Workflow run id to validate")
    return parser.parse_args()


def add_issue(issues: list[Issue], severity: str, check: str, detail: str) -> None:
    issues.append(Issue(severity=severity, check=check, detail=detail))


def summarize_issue_counts(issues: Iterable[Issue]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    return counts


def validate_stage_state(
    repo_root: Path,
    manifest: dict,
    state: dict,
    issues: list[Issue],
    allow_parallel: bool,
) -> None:
    manifest_ids = [stage["id"] for stage in manifest.get("stages", [])]
    state_ids = list(state.get("stages", {}).keys())
    if manifest_ids != state_ids:
        add_issue(
            issues,
            "error",
            "stage-registry",
            "Run state stage ids do not match the stage manifest order.",
        )

    stages = stage_index(manifest)
    in_progress = []
    for stage_id in manifest_ids:
        stage_state = state["stages"].get(stage_id)
        if stage_state is None:
            continue
        status = stage_state.get("status")
        if status == "in_progress":
            in_progress.append(stage_id)
        for dep in stage_state.get("depends_on", []):
            dep_state = state["stages"].get(dep)
            if dep_state is None:
                add_issue(issues, "error", "dependencies", f"Stage `{stage_id}` depends on missing stage `{dep}`.")
                continue
            if status == "completed" and dep_state.get("status") != "completed":
                add_issue(
                    issues,
                    "error",
                    "dependencies",
                    f"Stage `{stage_id}` is completed before dependency `{dep}` is completed.",
                )
        if status == "completed":
            missing = [rel for rel in stages[stage_id].get("outputs", []) if not (repo_root / rel).resolve().exists()]
            if missing:
                add_issue(
                    issues,
                    "error",
                    "stage-outputs",
                    f"Completed stage `{stage_id}` is missing outputs: {', '.join(missing)}.",
                )

    if not allow_parallel and len(in_progress) > 1:
        add_issue(
            issues,
            "error",
            "parallel-claims",
            f"Multiple stages are marked in progress while parallel claims are disabled: {', '.join(in_progress)}.",
        )


def validate_required_outputs(repo_root: Path, config: dict, issues: list[Issue]) -> None:
    for path in collect_required_output_paths(repo_root, config):
        if not path.exists():
            add_issue(issues, "error", "required-output", f"Missing required output: `{path}`.")


def validate_manifest_file(repo_root: Path, config: dict, issues: list[Issue]) -> None:
    manifest_path = (repo_root / runtime_config(config).get("stages_manifest", "writing-pipeline/runtime/stages.yaml")).resolve()
    if not manifest_path.is_file():
        add_issue(issues, "error", "stage-manifest", f"Missing machine-readable stage manifest: `{manifest_path}`.")


def validate_figure_manifest(repo_root: Path, config: dict, issues: list[Issue]) -> None:
    manifest_rel = config.get("deliverables", {}).get("figure_manifest_output")
    if not manifest_rel:
        add_issue(issues, "warning", "figure-manifest", "No figure manifest path is configured.")
        return
    manifest_path = (repo_root / manifest_rel).resolve()
    if not manifest_path.is_file():
        add_issue(issues, "error", "figure-manifest", f"Missing figure manifest: `{manifest_path}`.")
        return

    text = manifest_path.read_text(encoding="utf-8")
    for job in document_jobs(repo_root, config):
        markdown_path = job["markdown_path"]
        if markdown_path.is_file() and markdown_path.name not in text:
            add_issue(
                issues,
                "error",
                "figure-manifest",
                f"Figure manifest does not mention `{markdown_path.name}`.",
            )

    asset_paths = sorted(set(re.findall(r"`(/[^`]*outputs/assets/[^`]+)`", text)))
    for asset_path in asset_paths:
        if not Path(asset_path).is_file():
            add_issue(
                issues,
                "error",
                "figure-manifest-assets",
                f"Figure manifest references a missing asset: `{asset_path}`.",
            )


def validate_html_outputs(repo_root: Path, config: dict, issues: list[Issue]) -> None:
    for job in document_jobs(repo_root, config):
        if not job["required"]:
            continue
        html_path = job["html_path"]
        if not html_path.is_file():
            add_issue(issues, "error", "html-output", f"Missing rendered HTML output: `{html_path}`.")
            continue
        text = html_path.read_text(encoding="utf-8")
        img_sources = re.findall(r'<img[^>]+src="([^"]+)"', text)
        non_embedded = [src for src in img_sources if not src.startswith("data:")]
        if non_embedded:
            add_issue(
                issues,
                "error",
                "html-self-contained",
                f"HTML output `{html_path.name}` contains non-embedded image sources: {', '.join(non_embedded[:3])}.",
            )


def validate_translation_alignment(repo_root: Path, config: dict, issues: list[Issue]) -> None:
    for pair in translation_pairs(repo_root, config):
        source_path = pair["source"]["markdown_path"]
        target_path = pair["target"]["markdown_path"]
        if not source_path.is_file() or not target_path.is_file():
            add_issue(
                issues,
                "error",
                "translation-pair",
                f"Missing translation pair markdown: `{source_path}` or `{target_path}`.",
            )
            continue

        source_text = source_path.read_text(encoding="utf-8")
        target_text = target_path.read_text(encoding="utf-8")

        source_images = extract_image_targets(source_text)
        target_images = extract_image_targets(target_text)
        if source_images != target_images:
            add_issue(
                issues,
                "error",
                "translation-images",
                f"Image references differ between `{source_path.name}` and `{target_path.name}`.",
            )

        source_numbers = Counter(extract_numeric_tokens(source_text))
        target_numbers = Counter(extract_numeric_tokens(target_text))
        if source_numbers != target_numbers:
            add_issue(
                issues,
                "error",
                "translation-numbers",
                f"Numeric tokens differ between `{source_path.name}` and `{target_path.name}`.",
            )

        source_math = Counter(extract_markdown_math(source_text))
        target_math = Counter(extract_markdown_math(target_text))
        if source_math != target_math:
            add_issue(
                issues,
                "error",
                "translation-math",
                f"Math expressions differ between `{source_path.name}` and `{target_path.name}`.",
            )


def build_report(repo_root: Path, config: dict, run_id: str, state: dict, issues: list[Issue]) -> str:
    counts = summarize_issue_counts(issues)
    lines = [
        "# Workflow Validation Report",
        "",
        f"- Run id: `{run_id}`",
        f"- Repo root: `{repo_root}`",
        f"- Overall run status: `{state.get('status', 'unknown')}`",
        f"- Errors: {counts.get('error', 0)}",
        f"- Warnings: {counts.get('warning', 0)}",
        "",
        "## Checks",
        "",
    ]

    if not issues:
        lines.extend(["- All validation checks passed.", ""])
    else:
        for issue in issues:
            lines.extend(
                [
                    f"### {issue.severity.upper()}: {issue.check}",
                    "",
                    f"- {issue.detail}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Stage Status",
            "",
            "| Stage id | Status | Assigned agent |",
            "|---|---|---|",
        ]
    )
    manifest = load_stage_manifest(repo_root, config)
    for stage in manifest.get("stages", []):
        stage_id = stage["id"]
        payload = state["stages"].get(stage_id, {})
        lines.append(
            f"| `{stage_id}` | `{payload.get('status', 'missing')}` | `{payload.get('assigned_agent') or 'n/a'}` |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    repo_root = repo_root_from_config(config_path)
    manifest = load_stage_manifest(repo_root, config)
    state = load_run_state(repo_root, config, args.run_id)

    issues: list[Issue] = []
    validate_manifest_file(repo_root, config, issues)
    validate_required_outputs(repo_root, config, issues)
    validate_stage_state(
        repo_root,
        manifest,
        state,
        issues,
        allow_parallel=bool(runtime_config(config).get("allow_parallel_stage_claims", False)),
    )
    validate_figure_manifest(repo_root, config, issues)
    validate_html_outputs(repo_root, config, issues)
    validate_translation_alignment(repo_root, config, issues)

    report_text = build_report(repo_root, config, args.run_id, state, issues)
    report_path = validation_report_path(repo_root, config, args.run_id)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")
    counts = summarize_issue_counts(issues)
    state["validation"] = {
        "status": "failed" if counts.get("error", 0) else "passed",
        "last_validated_at": utc_now(),
        "report_path": str(report_path),
        "error_count": counts.get("error", 0),
        "warning_count": counts.get("warning", 0),
    }
    save_run_state(repo_root, config, args.run_id, state)

    print(report_path)
    if any(issue.severity == "error" for issue in issues):
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"validate_workflow.py failed: {exc}", file=sys.stderr)
        raise

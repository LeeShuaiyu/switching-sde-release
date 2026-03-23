#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
}

CHINESE_NUMBER_WORDS = {
    "零": "0",
    "一": "1",
    "二": "2",
    "两": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
    "十": "10",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def dump_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def repo_root_from_config(config_path: Path) -> Path:
    return config_path.resolve().parent.parent


def load_config(config_path: Path) -> dict[str, Any]:
    payload = load_yaml(config_path)
    if not isinstance(payload, dict):
        raise ValueError(f"Config must be a mapping: {config_path}")
    return payload


def runtime_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("runtime", {})


def runtime_path(repo_root: Path, config: dict[str, Any], key: str, default_rel: str) -> Path:
    rel = runtime_config(config).get(key, default_rel)
    return (repo_root / rel).resolve()


def runs_root(repo_root: Path, config: dict[str, Any]) -> Path:
    return runtime_path(repo_root, config, "runs_dir", "writing-pipeline/runs")


def run_dir(repo_root: Path, config: dict[str, Any], run_id: str) -> Path:
    return runs_root(repo_root, config) / run_id


def stage_manifest_path(repo_root: Path, config: dict[str, Any]) -> Path:
    return runtime_path(repo_root, config, "stages_manifest", "writing-pipeline/runtime/stages.yaml")


def load_stage_manifest(repo_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    path = stage_manifest_path(repo_root, config)
    payload = load_yaml(path)
    if not isinstance(payload, dict) or "stages" not in payload:
        raise ValueError(f"Invalid stage manifest: {path}")
    stages = payload.get("stages") or []
    ids = [stage.get("id") for stage in stages]
    if len(ids) != len(set(ids)):
        raise ValueError("Stage manifest contains duplicate stage ids")
    return payload


def stage_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {stage["id"]: stage for stage in manifest.get("stages", [])}


def document_jobs(repo_root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    docs = config.get("deliverables", {}).get("documents", [])
    for entry in docs:
        markdown_output = entry.get("markdown_output")
        html_output = entry.get("html_output")
        if not markdown_output or not html_output:
            continue
        jobs.append(
            {
                "id": entry.get("id") or Path(markdown_output).stem,
                "kind": entry.get("kind", "document"),
                "language": entry.get("language", "unknown"),
                "canonical": bool(entry.get("canonical", False)),
                "required": bool(entry.get("required", True)),
                "translation_of": entry.get("translation_of"),
                "markdown_path": (repo_root / markdown_output).resolve(),
                "html_path": (repo_root / html_output).resolve(),
            }
        )
    return jobs


def translation_pairs(repo_root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    jobs = {job["id"]: job for job in document_jobs(repo_root, config)}
    pairs = []
    for job in jobs.values():
        source_id = job.get("translation_of")
        if not source_id:
            continue
        source = jobs.get(source_id)
        if source is None:
            continue
        pairs.append({"source": source, "target": job})
    return pairs


def build_initial_run_state(
    repo_root: Path,
    config_path: Path,
    config: dict[str, Any],
    manifest: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    created_at = utc_now()
    stages_payload: dict[str, Any] = {}
    for stage in manifest.get("stages", []):
        stages_payload[stage["id"]] = {
            "label": stage["label"],
            "owners": deepcopy(stage.get("owners", [])),
            "depends_on": deepcopy(stage.get("depends_on", [])),
            "status": "pending",
            "subagent_mode": stage.get("subagent_mode", "serial"),
            "assigned_agent": None,
            "started_at": None,
            "completed_at": None,
            "last_updated_at": created_at,
            "notes": [],
            "missing_outputs": deepcopy(stage.get("outputs", [])),
        }

    return {
        "version": 1,
        "run_id": run_id,
        "created_at": created_at,
        "updated_at": created_at,
        "status": "initialized",
        "validation": {
            "status": "not_run",
            "last_validated_at": None,
            "report_path": None,
            "error_count": None,
            "warning_count": None,
        },
        "repo_root": str(repo_root),
        "config_path": str(config_path.resolve()),
        "stage_manifest_path": str(stage_manifest_path(repo_root, config)),
        "documents": [
            {
                "id": job["id"],
                "kind": job["kind"],
                "language": job["language"],
                "canonical": job["canonical"],
                "translation_of": job.get("translation_of"),
                "required": job["required"],
                "markdown_path": str(job["markdown_path"]),
                "html_path": str(job["html_path"]),
            }
            for job in document_jobs(repo_root, config)
        ],
        "stages": stages_payload,
    }


def state_filename(config: dict[str, Any]) -> str:
    return runtime_config(config).get("state_filename", "run_state.yaml")


def events_filename(config: dict[str, Any]) -> str:
    return runtime_config(config).get("events_filename", "events.jsonl")


def briefs_dirname(config: dict[str, Any]) -> str:
    return runtime_config(config).get("briefs_dirname", "briefs")


def validation_report_filename(config: dict[str, Any]) -> str:
    return runtime_config(config).get("validation_report_filename", "validation_report.md")


def run_state_path(repo_root: Path, config: dict[str, Any], run_id: str) -> Path:
    return run_dir(repo_root, config, run_id) / state_filename(config)


def events_path(repo_root: Path, config: dict[str, Any], run_id: str) -> Path:
    return run_dir(repo_root, config, run_id) / events_filename(config)


def briefs_dir(repo_root: Path, config: dict[str, Any], run_id: str) -> Path:
    return run_dir(repo_root, config, run_id) / briefs_dirname(config)


def validation_report_path(repo_root: Path, config: dict[str, Any], run_id: str) -> Path:
    return run_dir(repo_root, config, run_id) / validation_report_filename(config)


def load_run_state(repo_root: Path, config: dict[str, Any], run_id: str) -> dict[str, Any]:
    path = run_state_path(repo_root, config, run_id)
    if not path.is_file():
        raise FileNotFoundError(f"Missing run state: {path}")
    payload = load_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid run state: {path}")
    return payload


def save_run_state(repo_root: Path, config: dict[str, Any], run_id: str, state: dict[str, Any]) -> Path:
    path = run_state_path(repo_root, config, run_id)
    state["updated_at"] = utc_now()
    dump_yaml(path, state)
    return path


def append_event(repo_root: Path, config: dict[str, Any], run_id: str, event: dict[str, Any]) -> Path:
    path = events_path(repo_root, config, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(event)
    payload.setdefault("timestamp", utc_now())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path


def stage_outputs_missing(repo_root: Path, stage: dict[str, Any]) -> list[str]:
    missing = []
    for rel in stage.get("outputs", []):
        if not (repo_root / rel).resolve().exists():
            missing.append(rel)
    return missing


def stage_dependencies_satisfied(state: dict[str, Any], stage_id: str) -> bool:
    stage_state = state["stages"][stage_id]
    return all(state["stages"][dep]["status"] == "completed" for dep in stage_state.get("depends_on", []))


def next_runnable_stages(state: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    runnable: list[dict[str, Any]] = []
    stages = stage_index(manifest)
    for stage in manifest.get("stages", []):
        stage_id = stage["id"]
        status = state["stages"][stage_id]["status"]
        if status not in {"pending", "failed"}:
            continue
        if stage_dependencies_satisfied(state, stage_id):
            runnable.append(stages[stage_id])
    return runnable


def in_progress_stage_ids(state: dict[str, Any]) -> list[str]:
    return [stage_id for stage_id, payload in state["stages"].items() if payload["status"] == "in_progress"]


def mark_stage_claimed(
    state: dict[str, Any],
    stage_id: str,
    agent_name: str,
    allow_parallel: bool,
    note: str | None,
) -> None:
    if stage_id not in state["stages"]:
        raise KeyError(f"Unknown stage id: {stage_id}")
    if not stage_dependencies_satisfied(state, stage_id):
        raise ValueError(f"Stage dependencies not yet satisfied: {stage_id}")
    if not allow_parallel:
        active = [item for item in in_progress_stage_ids(state) if item != stage_id]
        if active:
            raise ValueError(f"Another stage is already in progress: {', '.join(active)}")
    stage_state = state["stages"][stage_id]
    stage_state["status"] = "in_progress"
    stage_state["assigned_agent"] = agent_name
    stage_state["started_at"] = stage_state.get("started_at") or utc_now()
    stage_state["last_updated_at"] = utc_now()
    if note:
        stage_state.setdefault("notes", []).append(note)
    state["status"] = "in_progress"


def mark_stage_completed(
    repo_root: Path,
    manifest: dict[str, Any],
    state: dict[str, Any],
    stage_id: str,
    note: str | None,
    skip_output_check: bool = False,
) -> list[str]:
    stages = stage_index(manifest)
    if stage_id not in stages:
        raise KeyError(f"Unknown stage id: {stage_id}")
    missing = [] if skip_output_check else stage_outputs_missing(repo_root, stages[stage_id])
    if missing:
        raise ValueError(f"Cannot complete stage {stage_id}; missing outputs: {', '.join(missing)}")
    stage_state = state["stages"][stage_id]
    stage_state["status"] = "completed"
    stage_state["completed_at"] = utc_now()
    stage_state["last_updated_at"] = utc_now()
    stage_state["missing_outputs"] = missing
    if note:
        stage_state.setdefault("notes", []).append(note)
    if all(payload["status"] == "completed" for payload in state["stages"].values()):
        state["status"] = "completed"
    else:
        state["status"] = "in_progress"
    return missing


def mark_stage_failed(state: dict[str, Any], stage_id: str, note: str | None) -> None:
    if stage_id not in state["stages"]:
        raise KeyError(f"Unknown stage id: {stage_id}")
    stage_state = state["stages"][stage_id]
    stage_state["status"] = "failed"
    stage_state["last_updated_at"] = utc_now()
    if note:
        stage_state.setdefault("notes", []).append(note)
    state["status"] = "in_progress"


def sync_state_from_outputs(repo_root: Path, manifest: dict[str, Any], state: dict[str, Any]) -> list[str]:
    changed: list[str] = []
    for stage in manifest.get("stages", []):
        stage_id = stage["id"]
        stage_state = state["stages"][stage_id]
        if stage_state["status"] == "completed":
            continue
        if not stage_dependencies_satisfied(state, stage_id):
            continue
        missing = stage_outputs_missing(repo_root, stage)
        stage_state["missing_outputs"] = missing
        if not missing:
            stage_state["status"] = "completed"
            stage_state["completed_at"] = stage_state.get("completed_at") or utc_now()
            stage_state["last_updated_at"] = utc_now()
            stage_state.setdefault("notes", []).append(
                "Auto-completed from existing filesystem outputs."
            )
            changed.append(stage_id)
    if all(payload["status"] == "completed" for payload in state["stages"].values()):
        state["status"] = "completed"
    elif any(payload["status"] == "completed" for payload in state["stages"].values()):
        state["status"] = "in_progress"
    return changed


def render_stage_brief(
    repo_root: Path,
    config: dict[str, Any],
    manifest: dict[str, Any],
    state: dict[str, Any],
    stage_id: str,
) -> str:
    stages = stage_index(manifest)
    if stage_id not in stages:
        raise KeyError(f"Unknown stage id: {stage_id}")
    stage = stages[stage_id]
    stage_state = state["stages"][stage_id]
    deps = stage.get("depends_on", [])
    dep_lines = []
    for dep in deps:
        dep_state = state["stages"].get(dep, {})
        dep_lines.append(f"- `{dep}`: {dep_state.get('status', 'unknown')}")
    if not dep_lines:
        dep_lines = ["- none"]

    read_lines = [f"- `{item}`" for item in stage.get("read_set", [])] or ["- none"]
    write_lines = [f"- `{item}`" for item in stage.get("write_scope", [])] or ["- none"]
    output_lines = [f"- `{item}`" for item in stage.get("outputs", [])] or ["- none"]
    check_lines = [f"- {item}" for item in stage.get("completion_checks", [])] or ["- none"]
    allow_parallel = runtime_config(config).get("allow_parallel_stage_claims", False)

    return "\n".join(
        [
            f"# Stage Brief: {stage['label']}",
            "",
            f"- Run id: `{state['run_id']}`",
            f"- Stage id: `{stage_id}`",
            f"- Current status: `{stage_state['status']}`",
            f"- Owners: {', '.join(f'`{owner}`' for owner in stage.get('owners', []))}",
            f"- Subagent mode: `{stage.get('subagent_mode', 'serial')}`",
            f"- Parallel stage claims allowed: `{str(allow_parallel).lower()}`",
            "",
            "## Purpose",
            "",
            stage.get("purpose", "No stage purpose recorded."),
            "",
            "## Dependencies",
            "",
            *dep_lines,
            "",
            "## Required Reads",
            "",
            *read_lines,
            "",
            "## Owned Write Scope",
            "",
            *write_lines,
            "",
            "## Required Outputs",
            "",
            *output_lines,
            "",
            "## Completion Checks",
            "",
            *check_lines,
            "",
            "## Codex Subagent Rules",
            "",
            "- You are not alone in the codebase.",
            "- Only edit the files listed in the owned write scope.",
            "- Do not revert another agent's changes.",
            "- Record assumptions or blockers in the completion note if anything remains uncertain.",
            "- Do not mark this stage complete unless every required output exists.",
            "",
            "## Runtime Paths",
            "",
            f"- Repo root: `{repo_root}`",
            f"- Run state: `{run_state_path(repo_root, config, state['run_id'])}`",
            f"- Validation report path: `{validation_report_path(repo_root, config, state['run_id'])}`",
        ]
    ) + "\n"


def write_stage_brief(
    repo_root: Path,
    config: dict[str, Any],
    manifest: dict[str, Any],
    state: dict[str, Any],
    stage_id: str,
) -> Path:
    brief_path = briefs_dir(repo_root, config, state["run_id"]) / f"{stage_id}.md"
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(
        render_stage_brief(repo_root, config, manifest, state, stage_id),
        encoding="utf-8",
    )
    return brief_path


def write_all_stage_briefs(
    repo_root: Path,
    config: dict[str, Any],
    manifest: dict[str, Any],
    state: dict[str, Any],
) -> list[Path]:
    paths = []
    for stage in manifest.get("stages", []):
        paths.append(write_stage_brief(repo_root, config, manifest, state, stage["id"]))
    return paths


def looks_like_math_token(raw: str) -> bool:
    text = raw.strip()
    if not text:
        return False
    if "\\" in text or "^" in text or "{" in text or "}" in text:
        return True
    if any(op in text for op in ("=", "<", ">")):
        return True
    if re.fullmatch(r"[A-Za-z]", text):
        return True
    if re.fullmatch(r"[A-Za-z]_[A-Za-z0-9]+", text):
        return True
    if re.fullmatch(r"[A-Z]_\d+", text):
        return True
    return False


def extract_markdown_math(text: str) -> list[str]:
    blocks = [item.strip() for item in re.findall(r"```math\s*(.*?)```", text, re.S)]
    inline = []
    for token in re.findall(r"`([^`]+)`", text):
        if looks_like_math_token(token):
            inline.append(token.strip())
    return blocks + inline


def extract_numeric_tokens(text: str) -> list[str]:
    digits = re.findall(r"(?<![A-Za-z])(\d+(?:\.\d+)?(?:e[+-]?\d+)?)(?![A-Za-z])", text)
    lowered = text.lower()
    patterns = [
        r"\b(" + "|".join(NUMBER_WORDS) + r")\s+(?:random\s+)?seeds?\b",
        r"\b(" + "|".join(NUMBER_WORDS) + r")\s+epochs?\b",
        r"\b(" + "|".join(NUMBER_WORDS) + r")\s+times\b",
        r"\b(" + "|".join(NUMBER_WORDS) + r")-layer\b",
    ]
    words = []
    for pattern in patterns:
        words.extend(NUMBER_WORDS[item] for item in re.findall(pattern, lowered))
    chinese_patterns = [
        r"([零一二两三四五六七八九十])倍",
        r"([零一二两三四五六七八九十])层",
        r"([零一二两三四五六七八九十])个随机种子",
    ]
    chinese_words = []
    for pattern in chinese_patterns:
        chinese_words.extend(CHINESE_NUMBER_WORDS[item] for item in re.findall(pattern, text))
    return digits + words + chinese_words


def extract_image_targets(text: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)


def collect_required_output_paths(repo_root: Path, config: dict[str, Any]) -> list[Path]:
    outputs: list[Path] = []
    deliverables = config.get("deliverables", {})
    simple_keys = [
        "dossier_output",
        "evidence_output",
        "final_readiness_output",
        "figure_manifest_output",
        "report_output",
        "paper_output",
        "report_zh_output",
        "paper_zh_output",
        "report_html_output",
        "paper_html_output",
        "report_zh_html_output",
        "paper_zh_html_output",
    ]
    for key in simple_keys:
        rel = deliverables.get(key)
        if rel:
            outputs.append((repo_root / rel).resolve())
    return outputs

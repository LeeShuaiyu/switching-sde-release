#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from workflow_runtime import (
    append_event,
    build_initial_run_state,
    load_config,
    load_run_state,
    load_stage_manifest,
    mark_stage_claimed,
    mark_stage_completed,
    mark_stage_failed,
    next_runnable_stages,
    repo_root_from_config,
    run_dir,
    runtime_config,
    save_run_state,
    sync_state_from_outputs,
    write_all_stage_briefs,
    write_stage_brief,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage writing-pipeline workflow runs.")
    parser.add_argument("--config", required=True, help="Path to writing-pipeline run_config.yaml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a new workflow run")
    init_parser.add_argument("--run-id", required=True, help="Stable id for the workflow run")

    sync_parser = subparsers.add_parser("sync", help="Mark stages complete when outputs already exist")
    sync_parser.add_argument("--run-id", required=True)

    status_parser = subparsers.add_parser("status", help="Show run status")
    status_parser.add_argument("--run-id", required=True)

    next_parser = subparsers.add_parser("next", help="Show next runnable stages")
    next_parser.add_argument("--run-id", required=True)

    brief_parser = subparsers.add_parser("brief", help="Generate per-stage Codex-subagent briefs")
    brief_parser.add_argument("--run-id", required=True)
    brief_parser.add_argument("--stage", help="Stage id to render. Omit to render all briefs.")

    claim_parser = subparsers.add_parser("claim", help="Claim a stage for a Codex subagent")
    claim_parser.add_argument("--run-id", required=True)
    claim_parser.add_argument("--stage", required=True)
    claim_parser.add_argument("--agent", required=True, help="Human-readable subagent or owner name")
    claim_parser.add_argument("--note", help="Optional note recorded in run state")

    complete_parser = subparsers.add_parser("complete", help="Complete a stage after outputs exist")
    complete_parser.add_argument("--run-id", required=True)
    complete_parser.add_argument("--stage", required=True)
    complete_parser.add_argument("--note", help="Completion note")
    complete_parser.add_argument(
        "--skip-output-check",
        action="store_true",
        help="Allow completion without checking output files. Use sparingly.",
    )

    fail_parser = subparsers.add_parser("fail", help="Mark a stage as failed")
    fail_parser.add_argument("--run-id", required=True)
    fail_parser.add_argument("--stage", required=True)
    fail_parser.add_argument("--note", required=True)

    return parser.parse_args()


def load_context(config_arg: str) -> tuple[Path, dict, dict]:
    config_path = Path(config_arg).resolve()
    config = load_config(config_path)
    repo_root = repo_root_from_config(config_path)
    manifest = load_stage_manifest(repo_root, config)
    return repo_root, config, manifest


def cmd_init(repo_root: Path, config: dict, manifest: dict, run_id: str) -> int:
    target_dir = run_dir(repo_root, config, run_id)
    if target_dir.exists():
        raise FileExistsError(f"Run already exists: {target_dir}")
    target_dir.mkdir(parents=True, exist_ok=False)
    state = build_initial_run_state(repo_root, Path(config["_config_path"]), config, manifest, run_id)
    save_run_state(repo_root, config, run_id, state)
    if runtime_config(config).get("codex_subagents", {}).get("generate_stage_briefs", True):
        write_all_stage_briefs(repo_root, config, manifest, state)
    append_event(
        repo_root,
        config,
        run_id,
        {"event": "init", "run_id": run_id, "message": "Initialized workflow run."},
    )
    print(f"Initialized run: {target_dir}")
    return 0


def cmd_sync(repo_root: Path, config: dict, manifest: dict, run_id: str) -> int:
    state = load_run_state(repo_root, config, run_id)
    changed = sync_state_from_outputs(repo_root, manifest, state)
    save_run_state(repo_root, config, run_id, state)
    write_all_stage_briefs(repo_root, config, manifest, state)
    append_event(
        repo_root,
        config,
        run_id,
        {"event": "sync", "changed_stages": changed, "message": "Synced stages from existing outputs."},
    )
    if changed:
        print("Synced stages:")
        for stage_id in changed:
            print(f"- {stage_id}")
    else:
        print("No stage status changed during sync.")
    return 0


def print_stage_table(state: dict, manifest: dict) -> None:
    print(f"Run id: {state['run_id']}")
    print(f"Overall status: {state['status']}")
    validation = state.get("validation", {})
    print(f"Validation status: {validation.get('status', 'not_run')}")
    print("")
    for stage in manifest.get("stages", []):
        stage_id = stage["id"]
        payload = state["stages"][stage_id]
        owners = ", ".join(stage.get("owners", []))
        print(f"- {stage_id}: {payload['status']} [{owners}]")


def cmd_status(repo_root: Path, config: dict, manifest: dict, run_id: str) -> int:
    state = load_run_state(repo_root, config, run_id)
    print_stage_table(state, manifest)
    runnable = next_runnable_stages(state, manifest)
    if runnable:
        print("")
        print("Next runnable stages:")
        for stage in runnable:
            print(f"- {stage['id']}: {stage['label']}")
    return 0


def cmd_next(repo_root: Path, config: dict, manifest: dict, run_id: str) -> int:
    state = load_run_state(repo_root, config, run_id)
    runnable = next_runnable_stages(state, manifest)
    if not runnable:
        print("No runnable stages. Check status or validation output.")
        return 0
    print("Runnable stages:")
    for stage in runnable:
        owners = ", ".join(stage.get("owners", []))
        print(f"- {stage['id']}: {stage['label']} [{owners}]")
    return 0


def cmd_brief(repo_root: Path, config: dict, manifest: dict, run_id: str, stage_id: str | None) -> int:
    state = load_run_state(repo_root, config, run_id)
    if stage_id:
        path = write_stage_brief(repo_root, config, manifest, state, stage_id)
        print(path)
    else:
        paths = write_all_stage_briefs(repo_root, config, manifest, state)
        for path in paths:
            print(path)
    return 0


def cmd_claim(repo_root: Path, config: dict, manifest: dict, run_id: str, stage_id: str, agent: str, note: str | None) -> int:
    state = load_run_state(repo_root, config, run_id)
    allow_parallel = bool(runtime_config(config).get("allow_parallel_stage_claims", False))
    mark_stage_claimed(state, stage_id, agent, allow_parallel, note)
    save_run_state(repo_root, config, run_id, state)
    path = write_stage_brief(repo_root, config, manifest, state, stage_id)
    append_event(
        repo_root,
        config,
        run_id,
        {"event": "claim", "stage_id": stage_id, "agent": agent, "note": note},
    )
    print(f"Claimed {stage_id} for {agent}")
    print(f"Brief: {path}")
    return 0


def cmd_complete(
    repo_root: Path,
    config: dict,
    manifest: dict,
    run_id: str,
    stage_id: str,
    note: str | None,
    skip_output_check: bool,
) -> int:
    state = load_run_state(repo_root, config, run_id)
    stage_state = state["stages"].get(stage_id)
    if stage_state is None:
        raise KeyError(f"Unknown stage id: {stage_id}")
    require_claim = bool(
        runtime_config(config).get("codex_subagents", {}).get("require_stage_claim_before_completion", True)
    )
    require_note = bool(
        runtime_config(config).get("codex_subagents", {}).get("require_completion_notes", True)
    )
    if require_claim and stage_state["status"] not in {"in_progress", "completed"}:
        raise ValueError(f"Stage must be claimed before completion: {stage_id}")
    if require_note and not note:
        raise ValueError("A completion note is required by the runtime configuration.")
    mark_stage_completed(repo_root, manifest, state, stage_id, note, skip_output_check=skip_output_check)
    save_run_state(repo_root, config, run_id, state)
    append_event(
        repo_root,
        config,
        run_id,
        {
            "event": "complete",
            "stage_id": stage_id,
            "agent": stage_state.get("assigned_agent"),
            "note": note,
            "skip_output_check": skip_output_check,
        },
    )
    print(f"Completed {stage_id}")
    return 0


def cmd_fail(repo_root: Path, config: dict, run_id: str, stage_id: str, note: str) -> int:
    state = load_run_state(repo_root, config, run_id)
    mark_stage_failed(state, stage_id, note)
    save_run_state(repo_root, config, run_id, state)
    append_event(repo_root, config, run_id, {"event": "fail", "stage_id": stage_id, "note": note})
    print(f"Marked {stage_id} as failed")
    return 0


def main() -> int:
    args = parse_args()
    repo_root, config, manifest = load_context(args.config)
    config["_config_path"] = str(Path(args.config).resolve())

    if args.command == "init":
        return cmd_init(repo_root, config, manifest, args.run_id)
    if args.command == "sync":
        return cmd_sync(repo_root, config, manifest, args.run_id)
    if args.command == "status":
        return cmd_status(repo_root, config, manifest, args.run_id)
    if args.command == "next":
        return cmd_next(repo_root, config, manifest, args.run_id)
    if args.command == "brief":
        return cmd_brief(repo_root, config, manifest, args.run_id, args.stage)
    if args.command == "claim":
        return cmd_claim(repo_root, config, manifest, args.run_id, args.stage, args.agent, args.note)
    if args.command == "complete":
        return cmd_complete(
            repo_root,
            config,
            manifest,
            args.run_id,
            args.stage,
            args.note,
            args.skip_output_check,
        )
    if args.command == "fail":
        return cmd_fail(repo_root, config, args.run_id, args.stage, args.note)
    raise ValueError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"run_workflow.py failed: {exc}", file=sys.stderr)
        raise

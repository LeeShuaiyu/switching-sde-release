#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path


def _run_step(name: str, cmd: list[str], cwd: Path, env: dict[str, str]) -> dict:
    started = time.time()
    proc = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True)
    ended = time.time()
    return {
        "name": name,
        "command": " ".join(shlex.quote(v) for v in cmd),
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "duration_sec": round(ended - started, 3),
        "stdout_tail": (proc.stdout or "")[-4000:],
        "stderr_tail": (proc.stderr or "")[-4000:],
    }


def _assert_paths(repo_root: Path) -> list[str]:
    required = [
        repo_root / "pyproject.toml",
        repo_root / "setup.py",
        repo_root / "src" / "switching_sde" / "cli" / "main.py",
        repo_root / "scripts" / "build_release_bundle.py",
        repo_root / "scripts" / "release_preflight.py",
        repo_root / "RELEASE_CHECKLIST.md",
    ]
    missing = [str(p) for p in required if not p.exists()]
    return missing


def _write_reports(out_dir: Path, payload: dict) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_file = out_dir / "preflight_summary.json"
    md_file = out_dir / "preflight_summary.md"
    json_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# Release Preflight Summary")
    lines.append("")
    lines.append(f"- Timestamp: `{payload['timestamp']}`")
    lines.append(f"- Repository: `{payload['repo_root']}`")
    lines.append(f"- Legacy root: `{payload['legacy_root']}`")
    lines.append(f"- Overall status: `{payload['status']}`")
    lines.append("")
    lines.append("## Steps")
    lines.append("")
    for step in payload["steps"]:
        mark = "PASS" if step["ok"] else "FAIL"
        lines.append(f"- `{mark}` `{step['name']}` ({step['duration_sec']}s)")
        lines.append(f"  - Command: `{step['command']}`")
        if not step["ok"]:
            err = (step.get("stderr_tail") or step.get("stdout_tail") or "").strip().replace("\n", " ")
            if err:
                lines.append(f"  - Error tail: `{err[:500]}`")

    md_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_file, md_file


def main() -> int:
    ap = argparse.ArgumentParser(description="Release preflight checks for switching-sde-release.")
    ap.add_argument("--legacy-root", required=True, help="Absolute path to legacy PENN repo.")
    ap.add_argument("--python", default=sys.executable, help="Python executable.")
    ap.add_argument("--suite", default="paper_full", choices=["paper_full", "p5", "p6"])
    ap.add_argument("--output-dir", default="reports/release")
    ap.add_argument("--skip-live", action="store_true", help="Skip auto live eval/viz checks.")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    legacy_root = Path(args.legacy_root).expanduser().resolve()
    out_dir = (repo_root / args.output_dir).resolve()

    missing = _assert_paths(repo_root)
    steps = []
    env = os.environ.copy()
    env["PYTHONPATH"] = str((repo_root / "src").resolve())
    env["LEGACY_PENN_ROOT"] = str(legacy_root)

    if missing:
        payload = {
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
            "repo_root": str(repo_root),
            "legacy_root": str(legacy_root),
            "status": "failed",
            "missing_required_paths": missing,
            "steps": [],
        }
        _write_reports(out_dir, payload)
        print("[fail] missing required paths:")
        for p in missing:
            print(" -", p)
        return 2

    commands = [
        ("unit_tests", [args.python, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
        ("cli_help", [args.python, "-m", "switching_sde.cli.main", "--help"]),
        (
            "artifacts_index",
            [args.python, "-m", "switching_sde.cli.main", "artifacts", "index", "--legacy-root", str(legacy_root)],
        ),
        (
            "artifacts_link",
            [args.python, "-m", "switching_sde.cli.main", "artifacts", "link", "--legacy-root", str(legacy_root)],
        ),
        (
            "benchmark_frozen",
            [
                args.python,
                "-m",
                "switching_sde.cli.main",
                "benchmark",
                "--suite",
                args.suite,
                "--mode",
                "frozen",
                "--legacy-root",
                str(legacy_root),
                "--output-root",
                str(repo_root / "reports" / "paper"),
            ],
        ),
        (
            "report_generate",
            [
                args.python,
                "-m",
                "switching_sde.cli.main",
                "report",
                "--suite",
                args.suite,
                "--legacy-root",
                str(legacy_root),
                "--output-root",
                str(repo_root / "reports" / "paper"),
            ],
        ),
        (
            "bundle_lite",
            [args.python, "scripts/build_release_bundle.py", "--mode", "lite", "--output", "dist/switching_sde_release_lite.tar.gz"],
        ),
        (
            "bundle_full",
            [args.python, "scripts/build_release_bundle.py", "--mode", "full", "--output", "dist/switching_sde_release_full.tar.gz"],
        ),
    ]

    if not args.skip_live:
        commands.extend(
            [
                (
                    "eval_auto",
                    [
                        args.python,
                        "-m",
                        "switching_sde.cli.main",
                        "eval",
                        "--experiment",
                        "id_nonlinear",
                        "--mode",
                        "auto",
                        "--legacy-root",
                        str(legacy_root),
                        "--output-dir",
                        str(repo_root / "reports" / "paper" / "eval_auto"),
                    ],
                ),
                (
                    "viz_auto",
                    [
                        args.python,
                        "-m",
                        "switching_sde.cli.main",
                        "viz",
                        "--experiment",
                        "id_nonlinear",
                        "--mode",
                        "auto",
                        "--legacy-root",
                        str(legacy_root),
                        "--output-dir",
                        str(repo_root / "reports" / "paper" / "figures_auto"),
                    ],
                ),
            ]
        )

    failed = False
    for name, cmd in commands:
        step = _run_step(name=name, cmd=cmd, cwd=repo_root, env=env)
        steps.append(step)
        print(f"[{'ok' if step['ok'] else 'fail'}] {name} ({step['duration_sec']}s)")
        if not step["ok"]:
            failed = True
            break

    payload = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(repo_root),
        "legacy_root": str(legacy_root),
        "status": "passed" if not failed else "failed",
        "steps": steps,
    }
    json_file, md_file = _write_reports(out_dir, payload)
    print(f"[info] summary json: {json_file}")
    print(f"[info] summary md: {md_file}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="One-shot migration helper from legacy PENN repo")
    ap.add_argument("--legacy-root", required=True)
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    cmds = [
        ["switching-sde", "artifacts", "index", "--legacy-root", args.legacy_root],
        ["switching-sde", "artifacts", "link", "--legacy-root", args.legacy_root],
        ["switching-sde", "benchmark", "--suite", "paper_full", "--mode", "frozen", "--legacy-root", args.legacy_root],
        ["switching-sde", "benchmark", "--suite", "p5", "--mode", "frozen", "--legacy-root", args.legacy_root],
        ["switching-sde", "benchmark", "--suite", "p6", "--mode", "frozen", "--legacy-root", args.legacy_root],
        ["switching-sde", "report", "--suite", "paper_full", "--legacy-root", args.legacy_root],
    ]

    for cmd in cmds:
        print("[run]", " ".join(cmd))
        subprocess.run(cmd, cwd=root, check=True)
    print("[ok] migration completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

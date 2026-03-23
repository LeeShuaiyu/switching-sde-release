#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess


def main() -> int:
    ap = argparse.ArgumentParser(description="Link legacy artifacts using switching-sde CLI")
    ap.add_argument("--legacy-root", required=True)
    args = ap.parse_args()

    subprocess.run(["switching-sde", "artifacts", "index", "--legacy-root", args.legacy_root], check=True)
    subprocess.run(["switching-sde", "artifacts", "link", "--legacy-root", args.legacy_root], check=True)
    print("[ok] linked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

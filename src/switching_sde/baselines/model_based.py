from __future__ import annotations

import subprocess
import sys

from switching_sde.utils.legacy_import import resolve_legacy_file


def run_paper_benchmarks(
    *,
    output_root: str = "",
    explicit_legacy_root: str = "",
) -> int:
    script = resolve_legacy_file("switching/run_paper_benchmarks.py", explicit_legacy_root)
    cmd = [sys.executable, str(script)]
    if output_root:
        cmd.extend(["--output-root", output_root])
    proc = subprocess.run(cmd, check=False)
    return int(proc.returncode)

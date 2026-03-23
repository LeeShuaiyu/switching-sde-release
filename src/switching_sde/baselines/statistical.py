from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from switching_sde.utils.legacy_import import resolve_legacy_file


def run_statistical_baselines(
    *,
    split: str = "test",
    output_dir: str = "",
    data_file: str = "",
    explicit_legacy_root: str = "",
) -> int:
    script = resolve_legacy_file("switching/run_statistical_baselines.py", explicit_legacy_root)
    cmd = [sys.executable, str(script), "--split", split]
    if output_dir:
        cmd.extend(["--output-dir", output_dir])
    if data_file:
        cmd.extend(["--data-file", data_file])
    proc = subprocess.run(cmd, check=False)
    return int(proc.returncode)

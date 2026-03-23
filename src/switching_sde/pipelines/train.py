from __future__ import annotations

import subprocess
import sys

from switching_sde.utils.legacy_import import resolve_legacy_file


def run_train(
    *,
    explicit_legacy_root: str = "",
    passthrough_args: list[str] | None = None,
) -> int:
    """Delegate training to legacy training script with transparent passthrough args."""
    script = resolve_legacy_file("switching/train_switching.py", explicit_legacy_root)
    cmd = [sys.executable, str(script)]
    if passthrough_args:
        cmd.extend(passthrough_args)
    proc = subprocess.run(cmd, check=False)
    return int(proc.returncode)

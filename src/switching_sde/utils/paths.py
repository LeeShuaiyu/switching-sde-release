from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def manifests_dir() -> Path:
    return repo_root() / "assets" / "manifests"


def reports_root() -> Path:
    return repo_root() / "reports" / "paper"


def legacy_root(explicit: str | None = None) -> Path:
    """Resolve legacy PENN repository root with portable priority.

    Priority:
    1) explicit CLI argument
    2) LEGACY_PENN_ROOT environment variable
    3) sibling directory: ../PENN
    4) local fallback: ./legacy/PENN
    """
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("LEGACY_PENN_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    candidates = [
        repo_root().parent / "PENN",
        repo_root() / "legacy" / "PENN",
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return candidates[0].resolve()

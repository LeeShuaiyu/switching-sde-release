from __future__ import annotations

import os
from pathlib import Path


def detect_legacy_root() -> Path:
    env = os.environ.get("LEGACY_PENN_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()

    # Common local default: sibling PENN repo
    repo_root = Path(__file__).resolve().parents[1]
    sibling = (repo_root.parent / "PENN").resolve()
    if sibling.exists():
        return sibling

    # Last-resort fallback path (may not exist; caller should guard)
    return sibling

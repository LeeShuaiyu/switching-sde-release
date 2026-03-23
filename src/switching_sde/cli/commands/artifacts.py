from __future__ import annotations

import os
import shutil
from collections import Counter
from pathlib import Path

from switching_sde.artifacts.legacy_adapter import build_dataset_lock, index_legacy_artifacts
from switching_sde.artifacts.resolver import linked_artifact_path
from switching_sde.artifacts.registry import save_registry
from switching_sde.data.io import write_json
from switching_sde.utils.logging import get_logger
from switching_sde.utils.paths import manifests_dir

logger = get_logger(__name__)


def cmd_index(args) -> int:
    legacy_root = Path(args.legacy_root).expanduser().resolve()
    out_lock = manifests_dir() / "artifacts.lock.json"
    out_data_lock = manifests_dir() / "datasets.lock.json"

    registry = index_legacy_artifacts(legacy_root)
    save_registry(out_lock, registry)
    dataset_payload = build_dataset_lock(legacy_root, out_data_lock)
    status_counts = Counter(r.status for r in registry.records)
    kind_counts = Counter(r.kind for r in registry.records)
    dataset_status_counts = Counter(d.get("status", "unknown") for d in dataset_payload.get("datasets", []))

    logger.info("Indexed %d artifacts", len(registry.records))
    logger.info("Artifact lock: %s", out_lock)
    logger.info("Dataset lock: %s", out_data_lock)

    write_json(
        manifests_dir() / "index_summary.json",
        {
            "legacy_root": str(legacy_root),
            "num_records": len(registry.records),
            "kind_counts": dict(kind_counts),
            "status_counts": dict(status_counts),
            "dataset_status_counts": dict(dataset_status_counts),
            "artifact_lock": str(out_lock),
            "dataset_lock": str(out_data_lock),
        },
    )
    return 0


def cmd_link(args) -> int:
    from switching_sde.artifacts.registry import load_registry

    lock = manifests_dir() / "artifacts.lock.json"
    reg = load_registry(lock)
    if not reg.records:
        if not args.legacy_root:
            raise FileNotFoundError(
                "Artifact lock is empty. Run `switching-sde artifacts index --legacy-root <path>` first "
                "or pass --legacy-root here."
            )
        legacy = Path(args.legacy_root).expanduser().resolve()
        reg = index_legacy_artifacts(legacy)
        save_registry(lock, reg)
    link_root = Path(args.link_root).expanduser().resolve() if args.link_root else (manifests_dir().parents[1] / "assets" / "linked")

    # Rebuild link tree to avoid stale links and basename collisions.
    if link_root.exists():
        shutil.rmtree(link_root)

    created = 0
    for r in reg.records:
        src = Path(r.path)
        if not src.exists():
            continue
        dst = linked_artifact_path(link_root, r)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() or dst.is_symlink():
            try:
                if dst.resolve() == src.resolve():
                    continue
            except Exception:
                pass
            dst.unlink()
        os.symlink(src, dst)
        created += 1

    logger.info("Linked %d artifacts into %s", created, link_root)
    return 0

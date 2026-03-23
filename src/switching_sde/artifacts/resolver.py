from __future__ import annotations

from pathlib import Path

from switching_sde.artifacts.registry import ArtifactRecord, ArtifactRegistry


def linked_artifact_path(link_root: Path, record: ArtifactRecord) -> Path:
    """Deterministic link path to avoid basename collisions across folders."""
    basename = Path(record.path).name
    return link_root / record.kind / f"{record.artifact_id}__{basename}"


class ArtifactResolver:
    def __init__(self, registry: ArtifactRegistry, repo_root: Path):
        self.registry = registry
        self.repo_root = repo_root
        self.link_root = repo_root / "assets" / "linked"

    def resolve(
        self,
        *,
        kind: str,
        scenario: str = "",
        method: str = "",
        seed: int | None = None,
        cli_path: str = "",
    ) -> Path | None:
        # 1) explicit CLI path
        if cli_path:
            p = Path(cli_path).expanduser()
            if p.exists():
                return p.resolve()

        # candidates from registry
        candidates = self.registry.filter(kind=kind)
        if scenario:
            candidates = [r for r in candidates if r.scenario == scenario]
        if method:
            candidates = [r for r in candidates if r.method == method]
        if seed is not None:
            candidates = [r for r in candidates if r.seed == seed]

        # Prefer ready records first.
        candidates = sorted(candidates, key=lambda r: (0 if r.status == "ready" else 1, r.path))

        # 2) linked local artifacts
        for r in candidates:
            linked = linked_artifact_path(self.link_root, r)
            if linked.exists():
                return linked.resolve()
            # Backward compatibility for old basename-only links.
            legacy_link = self.link_root / kind / Path(r.path).name
            if legacy_link.exists():
                return legacy_link.resolve()

        # 3) direct legacy/local path
        for r in candidates:
            p = Path(r.path)
            if p.exists():
                return p.resolve()

        # 4) fallback: any ready artifact of that kind
        fallback = [r for r in self.registry.records if r.kind == kind]
        fallback = sorted(fallback, key=lambda r: (0 if r.status == "ready" else 1, r.path))
        for r in fallback:
            p = Path(r.path)
            if p.exists():
                return p.resolve()
        return None

    def list_records(self, *, kind: str | None = None) -> list[ArtifactRecord]:
        if kind is None:
            return list(self.registry.records)
        return [r for r in self.registry.records if r.kind == kind]

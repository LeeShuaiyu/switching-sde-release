from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from switching_sde.data.io import read_json, write_json


@dataclass
class ArtifactRecord:
    artifact_id: str
    kind: str
    scenario: str
    method: str
    seed: int | None
    data_version: str
    split_hash: str
    path: str
    sha1: str
    status: str


@dataclass
class ArtifactRegistry:
    version: int
    legacy_root: str
    generated_at: str
    records: list[ArtifactRecord]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "legacy_root": self.legacy_root,
            "generated_at": self.generated_at,
            "records": [asdict(r) for r in self.records],
        }

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "ArtifactRegistry":
        recs = [ArtifactRecord(**r) for r in obj.get("records", [])]
        return cls(
            version=int(obj.get("version", 1)),
            legacy_root=str(obj.get("legacy_root", "")),
            generated_at=str(obj.get("generated_at", "")),
            records=recs,
        )

    def filter(
        self,
        *,
        kind: str | None = None,
        scenario: str | None = None,
        method: str | None = None,
        seed: int | None = None,
    ) -> list[ArtifactRecord]:
        out = []
        for r in self.records:
            if kind is not None and r.kind != kind:
                continue
            if scenario is not None and r.scenario != scenario:
                continue
            if method is not None and r.method != method:
                continue
            if seed is not None and r.seed != seed:
                continue
            out.append(r)
        return out


def load_registry(lock_path: str | Path) -> ArtifactRegistry:
    p = Path(lock_path)
    if not p.exists():
        return ArtifactRegistry(version=1, legacy_root="", generated_at="", records=[])
    return ArtifactRegistry.from_dict(read_json(p))


def save_registry(lock_path: str | Path, registry: ArtifactRegistry) -> None:
    write_json(lock_path, registry.to_dict())

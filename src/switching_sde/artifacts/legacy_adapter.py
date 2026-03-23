from __future__ import annotations

import datetime as dt
import hashlib
import re
from pathlib import Path

from switching_sde.artifacts.registry import ArtifactRecord, ArtifactRegistry
from switching_sde.data.io import read_json, write_json
from switching_sde.utils.hashing import sha1_file

_JSON_NAME = re.compile(r"(?P<scenario>[A-Za-z0-9_]+)_(?P<method>.+?)_seed(?P<seed>\d+)_test\.json$")


def _artifact_id(kind: str, path: Path) -> str:
    rel = str(path).replace("\\", "/")
    key = f"{kind}:{rel}"
    key_hash = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    file_hash = sha1_file(path)[:10] if path.exists() else "0" * 10
    return f"{key_hash}-{file_hash}"


def _safe_metric_str(obj: dict, key: str) -> str:
    v = obj.get(key, "")
    return str(v) if v is not None else ""


def _resolve_checkpoint_path(raw: str, legacy_root: Path) -> Path | None:
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        # Legacy payloads mostly use './...'
        p = (legacy_root / raw.lstrip("./")).resolve()
    return p


def _resolve_expected_test_dataset(data_version: str, legacy_root: Path) -> Path | None:
    if not data_version:
        return None
    data_root = legacy_root / "data" / "switching_ou"
    candidate = data_root / f"switching_ou_test_{data_version}.pkl"
    if candidate.exists():
        return candidate
    if data_version == "fixed_v2":
        fallback = data_root / "switching_ou_test.pkl"
        if fallback.exists():
            return fallback
        return fallback
    return candidate


def _record_from_eval_json(path: Path, legacy_root: Path) -> ArtifactRecord:
    payload = read_json(path)
    m = _JSON_NAME.search(path.name)
    scenario = payload.get("scenario", "")
    method = payload.get("method_id", "")
    seed = payload.get("seed", None)
    if m:
        scenario = scenario or m.group("scenario")
        method = method or m.group("method")
        if seed is None:
            seed = int(m.group("seed"))
    if seed is not None:
        try:
            seed = int(seed)
        except Exception:
            seed = None

    ckpt_path = _resolve_checkpoint_path(str(payload.get("checkpoint", "")), legacy_root)
    data_version = _safe_metric_str(payload, "data_version")
    expected_test_dataset = _resolve_expected_test_dataset(data_version, legacy_root)

    status = "ready"
    if not path.exists():
        status = "missing_required"
    elif ckpt_path is not None and not ckpt_path.exists():
        # Frozen replay can still work from existing eval json; mark as optional miss for live.
        status = "missing_optional"
    elif expected_test_dataset is not None and not expected_test_dataset.exists():
        status = "missing_optional"

    return ArtifactRecord(
        artifact_id=_artifact_id("eval_json", path),
        kind="eval_json",
        scenario=str(scenario or ""),
        method=str(method or ""),
        seed=seed,
        data_version=data_version,
        split_hash=_safe_metric_str(payload, "split_hash"),
        path=str(path.resolve()),
        sha1=sha1_file(path),
        status=status,
    )


def _record_generic(kind: str, path: Path, *, scenario: str = "", method: str = "", seed: int | None = None) -> ArtifactRecord:
    return ArtifactRecord(
        artifact_id=_artifact_id(kind, path),
        kind=kind,
        scenario=scenario,
        method=method,
        seed=seed,
        data_version="",
        split_hash="",
        path=str(path.resolve()),
        sha1=sha1_file(path),
        status="ready" if path.exists() else "missing_optional",
    )


def _infer_checkpoint_info(path: Path) -> tuple[str, str, int | None]:
    name = path.parent.parent.name if path.parent.name == "model" else path.parent.name
    scenario = ""
    method = name
    seed = None

    m_seed = re.search(r"seed(\d+)", name)
    if m_seed:
        seed = int(m_seed.group(1))

    if name.startswith("p5_"):
        parts = name.split("_")
        if len(parts) >= 3:
            scenario = parts[1].upper()
            method = "_".join(parts[2:])
    elif name.startswith("p6_"):
        parts = name.split("_")
        if len(parts) >= 3:
            tag = parts[1]
            scenario = "ID_NL" if tag == "id" else f"OOD_NL{tag[-1]}" if tag.startswith("s") else ""
            method = "_".join(parts[2:])
    elif "switching_ou_" in name:
        method = name

    method = re.sub(r"_seed\d+(_smoke)?$", "", method)
    return scenario, method, seed


def index_legacy_artifacts(legacy_root: Path) -> ArtifactRegistry:
    records: list[ArtifactRecord] = []

    reports_root = legacy_root / "reports"
    data_root = legacy_root / "data" / "switching_ou"

    for p in sorted(reports_root.glob("**/*.json")):
        if p.name.endswith("_test.json") and "eval_json" in str(p):
            try:
                records.append(_record_from_eval_json(p, legacy_root))
            except Exception:
                records.append(_record_generic("eval_json", p))
        elif p.name in {
            "benchmark_summary_full.json",
            "benchmark_summary_full_v2.json",
            "benchmark_summary_p3.json",
            "benchmark_summary.json",
            "benchmark_ood_nl_full_table.json",
        }:
            records.append(_record_generic("table", p))
        else:
            # keep additional JSONs discoverable for frozen reporting
            if any(tok in str(p) for tok in ["paper_full", "p5", "p6_nonlinear", "autodl_p2"]):
                records.append(_record_generic("json", p))

    for p in sorted(reports_root.glob("**/*.csv")):
        if any(tok in p.name for tok in ["benchmark", "table", "summary", "stability", "quality", "degradation"]):
            records.append(_record_generic("table", p))

    for p in sorted(reports_root.glob("**/*.png")):
        records.append(_record_generic("figure", p))

    for p in sorted(reports_root.glob("**/*.ipynb")):
        records.append(_record_generic("notebook", p))

    for p in sorted(data_root.glob("**/best.ckpt")):
        scenario, method, seed = _infer_checkpoint_info(p)
        records.append(
            ArtifactRecord(
                artifact_id=_artifact_id("checkpoint", p),
                kind="checkpoint",
                scenario=scenario,
                method=method,
                seed=seed,
                data_version="",
                split_hash="",
                path=str(p.resolve()),
                sha1=sha1_file(p),
                status="ready",
            )
        )

    # dataset artifacts
    for p in sorted(data_root.glob("**/*.pkl")):
        records.append(_record_generic("dataset", p))

    generated_at = dt.datetime.now().isoformat(timespec="seconds")
    return ArtifactRegistry(version=1, legacy_root=str(legacy_root.resolve()), generated_at=generated_at, records=records)


def build_dataset_lock(legacy_root: Path, out_file: Path) -> dict:
    data_root = legacy_root / "data" / "switching_ou"
    datasets = []
    for p in sorted(data_root.glob("**/*.pkl")):
        datasets.append(
            {
                "path": str(p.resolve()),
                "sha1": sha1_file(p),
                "status": "ready" if p.exists() else "missing_required",
            }
        )

    # Also track expected test datasets referenced by eval payloads.
    expected_versions = set()
    for p in sorted((legacy_root / "reports").glob("**/*_test.json")):
        try:
            obj = read_json(p)
        except Exception:
            continue
        dv = str(obj.get("data_version", "")).strip()
        if dv:
            expected_versions.add(dv)
    for dv in sorted(expected_versions):
        expected = data_root / f"switching_ou_test_{dv}.pkl"
        status = "ready" if expected.exists() else "missing_optional"
        datasets.append(
            {
                "path": str(expected.resolve()),
                "sha1": sha1_file(expected),
                "status": status,
                "expected_from_eval_json": True,
            }
        )

    payload = {
        "version": 1,
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "datasets": datasets,
    }
    write_json(out_file, payload)
    return payload

from __future__ import annotations

from pathlib import Path

from switching_sde.pipelines.benchmark import run_benchmark
from switching_sde.utils.paths import legacy_root, repo_root


def cmd_benchmark(args) -> int:
    legacy = legacy_root(args.legacy_root)
    out_root = Path(args.output_root).expanduser().resolve() if args.output_root else (repo_root() / "reports" / "paper" / args.suite)
    payload = run_benchmark(suite=args.suite, mode=args.mode, legacy_root=legacy, output_root=out_root)
    print(f"[ok] benchmark {args.suite} ({payload.get('mode')}) -> {out_root}")
    return 0

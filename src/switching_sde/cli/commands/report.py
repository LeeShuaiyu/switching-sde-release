from __future__ import annotations

from pathlib import Path

from switching_sde.pipelines.report import generate_report
from switching_sde.utils.paths import legacy_root, repo_root


def cmd_report(args) -> int:
    legacy = legacy_root(args.legacy_root)
    out_root = Path(args.output_root).expanduser().resolve() if args.output_root else (repo_root() / "reports" / "paper")
    md = generate_report(suite=args.suite, legacy_root=legacy, output_root=out_root)
    print(f"[ok] report generated: {md}")
    return 0

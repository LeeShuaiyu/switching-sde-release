from __future__ import annotations

from pathlib import Path

from switching_sde.artifacts.frozen_loader import load_suite_tables, summarize_table


def generate_report(*, suite: str, legacy_root: Path, output_root: Path) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    md = output_root / f"{suite}_report.md"
    tables = load_suite_tables(legacy_root, suite)

    lines = []
    lines.append(f"# {suite} Reproduction Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("This report is generated in frozen mode from legacy benchmark artifacts.")
    lines.append("")

    for key, payload in tables.items():
        rows = payload["rows"]
        summary = summarize_table(rows)
        lines.append(f"## Table: {key}")
        lines.append(f"- Source: {payload['path']}")
        lines.append(f"- Rows: {summary.get('num_rows', 0)}")
        for sk, sv in sorted(summary.items()):
            if sk == "num_rows":
                continue
            lines.append(f"- {sk}: {sv}")
        lines.append("")

    md.write_text("\n".join(lines), encoding="utf-8")
    return md

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import datetime as dt
import html
import mimetypes
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


CAPTION_PREFIX_RE = re.compile(r"^(Figure|Table|图|表)\s*\d+\.")


FALLBACK_CSS = """
body { margin: 2rem auto; max-width: 980px; font-family: Georgia, serif; line-height: 1.7; color: #1f1a17; background: #f7f3eb; }
img { max-width: 100%; height: auto; }
figure { margin: 2rem 0; }
figcaption { color: #5a5147; font-size: 0.95rem; }
pre { background: #efe8dc; padding: 1rem; overflow-x: auto; }
code { font-family: Menlo, monospace; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #cfbea5; padding: 0.55rem 0.7rem; text-align: left; vertical-align: top; }
thead th { background: #eadcc7; }
"""


@dataclass
class Block:
    kind: str
    value: Any


class MarkdownRenderer:
    def __init__(
        self,
        markdown_path: Path,
        css_text: str,
        include_toc: bool,
        self_contained: bool,
        math_head: str,
        document_language: str,
    ):
        self.markdown_path = markdown_path
        self.css_text = css_text
        self.include_toc = include_toc
        self.self_contained = self_contained
        self.math_head = math_head
        self.document_language = document_language
        self.slug_counts: dict[str, int] = {}
        self.headings: list[tuple[int, str, str]] = []

    def render_document(self) -> str:
        text = self.markdown_path.read_text(encoding="utf-8")
        blocks = self._tokenize(text.splitlines())
        body = self._render_blocks(blocks)
        title = self._extract_title(blocks)
        deck = self._extract_deck(blocks)
        deck_html = self._render_inline(deck)
        toc = self._render_toc()
        source_path = html.escape(str(self.markdown_path))
        rendered_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        lang_code = self._document_lang_code()
        eyebrow = "写作流水线渲染输出" if self._is_chinese_document() else "Writing Pipeline Render"
        meta = self._render_meta_text(source_path, rendered_at)
        return f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{self.css_text}</style>
  {self.math_head}
</head>
<body>
  <div class="page-shell">
    <header class="masthead">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{html.escape(title)}</h1>
      <p class="deck">{deck_html}</p>
      <p class="meta">{meta}</p>
    </header>
    <div class="layout">
      {toc}
      <main class="document">
        {body}
      </main>
    </div>
  </div>
</body>
</html>
"""

    def _tokenize(self, lines: list[str]) -> list[Block]:
        blocks: list[Block] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue

            if stripped.startswith("```"):
                lang = stripped[3:].strip()
                i += 1
                code_lines: list[str] = []
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1
                blocks.append(Block("code", {"lang": lang, "text": "\n".join(code_lines)}))
                continue

            heading = re.match(r"^(#{1,6})\s+(.*)$", line)
            if heading:
                blocks.append(
                    Block(
                        "heading",
                        {"level": len(heading.group(1)), "text": heading.group(2).strip()},
                    )
                )
                i += 1
                continue

            image = re.match(r"^!\[(.*?)\]\((.*?)\)\s*$", stripped)
            if image:
                blocks.append(Block("image", {"alt": image.group(1), "src": image.group(2)}))
                i += 1
                continue

            if stripped in {"---", "***"}:
                blocks.append(Block("hr", None))
                i += 1
                continue

            if self._is_table_start(lines, i):
                table_lines: list[str] = []
                while i < len(lines) and lines[i].strip():
                    table_lines.append(lines[i].rstrip())
                    i += 1
                blocks.append(Block("table", self._parse_table(table_lines)))
                continue

            ordered = re.match(r"^\d+\.\s+", stripped)
            if ordered:
                items: list[str] = []
                while i < len(lines) and lines[i].strip():
                    match = re.match(r"^\d+\.\s+(.*)$", lines[i].strip())
                    if not match:
                        break
                    items.append(match.group(1))
                    i += 1
                blocks.append(Block("olist", items))
                continue

            unordered = re.match(r"^-\s+", stripped)
            if unordered:
                items = []
                while i < len(lines) and lines[i].strip():
                    match = re.match(r"^-\s+(.*)$", lines[i].strip())
                    if not match:
                        break
                    items.append(match.group(1))
                    i += 1
                blocks.append(Block("ulist", items))
                continue

            paragraph_lines = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip() and not self._starts_special(lines, i):
                paragraph_lines.append(lines[i].strip())
                i += 1
            blocks.append(Block("paragraph", " ".join(paragraph_lines)))

        return blocks

    def _starts_special(self, lines: list[str], index: int) -> bool:
        stripped = lines[index].strip()
        if not stripped:
            return True
        if stripped.startswith("```"):
            return True
        if re.match(r"^(#{1,6})\s+", lines[index]):
            return True
        if re.match(r"^!\[(.*?)\]\((.*?)\)\s*$", stripped):
            return True
        if stripped in {"---", "***"}:
            return True
        if re.match(r"^\d+\.\s+", stripped):
            return True
        if re.match(r"^-\s+", stripped):
            return True
        if self._is_table_start(lines, index):
            return True
        return False

    def _is_table_start(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines):
            return False
        first = lines[index].strip()
        second = lines[index + 1].strip()
        return "|" in first and self._is_table_separator(second)

    def _is_table_separator(self, line: str) -> bool:
        parts = [cell.strip() for cell in line.strip("|").split("|")]
        if not parts:
            return False
        return all(bool(re.fullmatch(r":?-{3,}:?", cell)) for cell in parts)

    def _parse_table(self, lines: list[str]) -> dict[str, list[list[str]]]:
        rows = []
        for raw in lines:
            if self._is_table_separator(raw.strip()):
                continue
            cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
            rows.append(cells)
        if not rows:
            return {"header": [], "rows": []}
        return {"header": rows[0], "rows": rows[1:]}

    def _extract_title(self, blocks: list[Block]) -> str:
        for block in blocks:
            if block.kind == "heading" and block.value["level"] == 1:
                return block.value["text"]
        return self.markdown_path.stem

    def _extract_deck(self, blocks: list[Block]) -> str:
        for block in blocks:
            if block.kind == "paragraph":
                return block.value
        return "Rendered writing-pipeline output."

    def _slugify(self, text: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
        count = self.slug_counts.get(base, 0)
        self.slug_counts[base] = count + 1
        return base if count == 0 else f"{base}-{count + 1}"

    def _render_toc(self) -> str:
        if not self.include_toc or not self.headings:
            return ""
        items = []
        for level, text, slug in self.headings:
            if level == 1:
                continue
            items.append(
                f'<li class="toc-level-{level}"><a href="#{slug}">{html.escape(text)}</a></li>'
            )
        if not items:
            return ""
        toc_title = "本页目录" if self._is_chinese_document() else "On This Page"
        return f'<aside class="toc"><h2>{toc_title}</h2><ul>' + "".join(items) + "</ul></aside>"

    def _render_blocks(self, blocks: list[Block]) -> str:
        pieces: list[str] = []
        i = 0
        while i < len(blocks):
            block = blocks[i]
            if block.kind == "heading":
                level = block.value["level"]
                text = block.value["text"]
                slug = self._slugify(text)
                self.headings.append((level, text, slug))
                pieces.append(f'<h{level} id="{slug}">{html.escape(text)}</h{level}>')
            elif block.kind == "paragraph":
                pieces.append(f"<p>{self._render_inline(block.value)}</p>")
            elif block.kind == "code":
                lang = block.value["lang"]
                if lang == "math":
                    pieces.append(self._render_math_block(block.value["text"]))
                else:
                    code_text = html.escape(block.value["text"])
                    lang_class = f' class="language-{html.escape(lang)}"' if lang else ""
                    pieces.append(f"<pre><code{lang_class}>{code_text}</code></pre>")
            elif block.kind == "image":
                caption = None
                if i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    if next_block.kind == "paragraph" and CAPTION_PREFIX_RE.match(next_block.value):
                        caption = next_block.value
                        i += 1
                pieces.append(self._render_figure(block.value["src"], block.value["alt"], caption))
            elif block.kind == "table":
                pieces.append(self._render_table(block.value))
            elif block.kind == "ulist":
                items = "".join(f"<li>{self._render_inline(item)}</li>" for item in block.value)
                pieces.append(f"<ul>{items}</ul>")
            elif block.kind == "olist":
                items = "".join(f"<li>{self._render_inline(item)}</li>" for item in block.value)
                pieces.append(f"<ol>{items}</ol>")
            elif block.kind == "hr":
                pieces.append("<hr>")
            i += 1
        return "\n".join(pieces)

    def _render_table(self, table: dict[str, list[list[str]]]) -> str:
        header = "".join(f"<th>{self._render_inline(cell)}</th>" for cell in table["header"])
        rows = []
        for row in table["rows"]:
            row_html = "".join(f"<td>{self._render_inline(cell)}</td>" for cell in row)
            rows.append(f"<tr>{row_html}</tr>")
        return (
            '<div class="table-wrap"><table><thead><tr>'
            + header
            + "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div>"
        )

    def _render_math_block(self, text: str) -> str:
        return f'<div class="math-block">\\[{html.escape(text.strip())}\\]</div>'

    def _render_figure(self, src: str, alt: str, caption: str | None) -> str:
        resolved_src = self._resolve_image_src(src)
        caption_html = ""
        if caption:
            caption_html = f"<figcaption>{self._render_inline(caption)}</figcaption>"
        elif alt:
            caption_html = f"<figcaption>{html.escape(alt)}</figcaption>"
        return (
            '<figure class="figure-card">'
            + f'<img src="{resolved_src}" alt="{html.escape(alt)}">'
            + caption_html
            + "</figure>"
        )

    def _resolve_image_src(self, src: str) -> str:
        if src.startswith("data:"):
            return src
        if src.startswith("http://") or src.startswith("https://"):
            if self.self_contained:
                raise ValueError(f"External image URLs are not allowed in self-contained mode: {src}")
            return html.escape(src)

        image_path = Path(src)
        if not image_path.is_absolute():
            image_path = (self.markdown_path.parent / image_path).resolve()

        if not image_path.is_file():
            raise FileNotFoundError(f"Missing figure asset: {image_path}")

        if not self.self_contained:
            return html.escape(str(image_path))

        mime_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
        payload = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{payload}"

    def _render_inline(self, text: str) -> str:
        placeholders: dict[str, str] = {}

        def stash(pattern: str, value_builder):
            nonlocal text

            def replace(match: re.Match[str]) -> str:
                token = f"@@TOKEN{len(placeholders)}@@"
                placeholders[token] = value_builder(match)
                return token

            text = re.sub(pattern, replace, text)

        stash(
            r"`([^`]+)`",
            lambda m: self._render_inline_code_or_math(m.group(1)),
        )
        escaped = html.escape(text)
        escaped = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
            escaped,
        )
        escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
        escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
        for token, rendered in placeholders.items():
            escaped = escaped.replace(html.escape(token), rendered)
            escaped = escaped.replace(token, rendered)
        return escaped

    def _render_inline_code_or_math(self, raw: str) -> str:
        if self._looks_like_math_span(raw):
            return f'<span class="math-inline">\\({html.escape(raw.strip())}\\)</span>'
        return f"<code>{html.escape(raw)}</code>"

    def _looks_like_math_span(self, raw: str) -> bool:
        text = raw.strip()
        if not text:
            return False
        if "\\" in text or "^" in text or "{" in text or "}" in text:
            return True
        if any(op in text for op in ("=", "<", ">")):
            return True
        if re.fullmatch(r"[A-Za-z]", text):
            return True
        if re.fullmatch(r"[A-Za-z]_[A-Za-z0-9]+", text):
            return True
        if re.fullmatch(r"[A-Z]_\d+", text):
            return True
        if re.fullmatch(r"[A-Za-z]_[A-Za-z0-9]+\s*=\s*.+", text):
            return True
        if re.fullmatch(r"[A-Za-z]\s*=\s*.+", text):
            return True
        if re.fullmatch(r"[A-Za-z0-9_]+\([^)]*\)\s*=\s*.+", text):
            return True
        if re.fullmatch(r"[A-Za-z0-9_]+\([^)]*\)", text):
            return True
        return False

    def _is_chinese_document(self) -> bool:
        lowered = self.document_language.lower()
        return lowered.startswith("chinese") or lowered.startswith("zh")

    def _document_lang_code(self) -> str:
        return "zh-CN" if self._is_chinese_document() else "en"

    def _render_meta_text(self, source_path: str, rendered_at: str) -> str:
        if self._is_chinese_document():
            return (
                f"此文件由 {source_path} 于 {rendered_at} 渲染生成。"
                "Markdown 仍然是可编辑的源文档。"
            )
        return (
            f"Rendered from {source_path} on {rendered_at}. "
            "Markdown remains the editable source of truth."
        )


def load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_css(repo_root: Path, config: dict[str, Any]) -> str:
    css_path = config.get("rendering", {}).get("html", {}).get("theme_css")
    if not css_path:
        return FALLBACK_CSS
    resolved = (repo_root / css_path).resolve()
    if resolved.is_file():
        return resolved.read_text(encoding="utf-8")
    return FALLBACK_CSS


def read_math_head(repo_root: Path, config: dict[str, Any]) -> str:
    math_cfg = config.get("rendering", {}).get("math", {})
    if not math_cfg.get("enabled", False):
        return ""

    config_script = """
<script>
window.MathJax = {
  tex: {
    inlineMath: [['\\\\(','\\\\)'], ['$', '$']],
    displayMath: [['\\\\[','\\\\]'], ['$$', '$$']],
    processEscapes: true
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
  },
  svg: {
    fontCache: 'global'
  }
};
</script>
""".strip()

    bundle_rel = math_cfg.get("bundle_js")
    if bundle_rel:
        bundle_path = (repo_root / bundle_rel).resolve()
        if bundle_path.is_file():
            bundle_text = bundle_path.read_text(encoding="utf-8")
            return config_script + "\n<script>\n" + bundle_text + "\n</script>"

    cdn_url = math_cfg.get("cdn_url")
    if cdn_url:
        return config_script + f'\n<script id="MathJax-script" async src="{html.escape(cdn_url, quote=True)}"></script>'

    return config_script


def collect_figure_references(markdown_path: Path) -> list[dict[str, str | int | None]]:
    refs: list[dict[str, str | int | None]] = []
    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines, start=1):
        match = re.match(r"!\[(.*?)\]\((.*?)\)\s*$", line.strip())
        if not match:
            continue
        alt = match.group(1)
        src = match.group(2)
        figure_label_match = re.match(r"^(Figure|图)\s*\d+", alt)
        figure_label = figure_label_match.group(1) if figure_label_match else alt
        caption_line = None
        for j in range(idx, len(lines)):
            candidate = lines[j].strip()
            if not candidate:
                continue
            if CAPTION_PREFIX_RE.match(candidate):
                caption_line = j + 1
            break
        image_path = Path(src)
        if not image_path.is_absolute():
            image_path = (markdown_path.parent / image_path).resolve()
        refs.append(
            {
                "figure_label": figure_label,
                "image_line": idx,
                "caption_line": caption_line,
                "asset_path": str(image_path),
            }
        )
    return refs


def get_document_jobs(repo_root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    deliverables = config.get("deliverables", {})
    docs_cfg = deliverables.get("documents", [])
    jobs: list[dict[str, Any]] = []
    if docs_cfg:
        for entry in docs_cfg:
            markdown_rel = entry.get("markdown_output")
            html_rel = entry.get("html_output")
            if not markdown_rel or not html_rel:
                continue
            jobs.append(
                {
                    "id": entry.get("id") or Path(markdown_rel).stem,
                    "language": entry.get("language", "unknown"),
                    "kind": entry.get("kind", "document"),
                    "required": bool(entry.get("required", True)),
                    "markdown_path": (repo_root / markdown_rel).resolve(),
                    "html_path": (repo_root / html_rel).resolve(),
                    "display_name": Path(markdown_rel).name,
                }
            )
        return jobs

    return [
        {
            "id": "report_en",
            "language": "English",
            "kind": "report",
            "required": True,
            "markdown_path": (repo_root / deliverables["report_output"]).resolve(),
            "html_path": (repo_root / deliverables["report_html_output"]).resolve(),
            "display_name": "report.md",
        },
        {
            "id": "paper_en",
            "language": "English",
            "kind": "paper",
            "required": True,
            "markdown_path": (repo_root / deliverables["paper_output"]).resolve(),
            "html_path": (repo_root / deliverables["paper_html_output"]).resolve(),
            "display_name": "paper_sections.md",
        },
    ]


def build_figure_manifest(repo_root: Path, config: dict[str, Any], jobs: list[dict[str, Any]]) -> str:
    output_assets_dir = config.get("writing", {}).get("visuals", {}).get(
        "output_assets_dir", "writing-pipeline/outputs/assets"
    )

    all_refs: dict[str, list[dict[str, str | int | None]]] = {}
    asset_usage: dict[str, set[str]] = {}
    existing_jobs = [job for job in jobs if job["markdown_path"].is_file()]
    for job in existing_jobs:
        label = job["display_name"]
        path = job["markdown_path"]
        refs = collect_figure_references(path)
        all_refs[label] = refs
        for ref in refs:
            asset_usage.setdefault(str(ref["asset_path"]), set()).add(label)

    lines = [
        "# Figure Manifest",
        "",
        "This manifest lists every figure cited by the current output drafts across all configured languages. It records both where the figure asset is stored under `writing-pipeline/outputs/assets/` and where the figure is cited inside the final markdown outputs.",
        "",
        "## Output Asset Directory",
        "",
        f"- `{(repo_root / output_assets_dir).resolve()}`",
        "",
        "## Unique Output Figure Assets",
        "",
        "| Output asset | Used in |",
        "|---|---|",
    ]
    for asset_path in sorted(asset_usage):
        used_in = ", ".join(f"`{name}`" for name in sorted(asset_usage[asset_path]))
        lines.append(f"| `{asset_path}` | {used_in} |")

    for job in existing_jobs:
        label = job["display_name"]
        path = job["markdown_path"]
        lines.extend(
            [
                "",
                f"## Citations in `{label}` ({job['language']})",
                "",
                "| Figure label | Image tag location | Caption location | Output asset |",
                "|---|---|---|---|",
            ]
        )
        for ref in all_refs[label]:
            image_loc = f"`{path.resolve()}:{ref['image_line']}`"
            caption_line = ref["caption_line"]
            caption_loc = f"`{path.resolve()}:{caption_line}`" if caption_line else "`n/a`"
            lines.append(
                f"| {ref['figure_label']} | {image_loc} | {caption_loc} | `{ref['asset_path']}` |"
            )

    return "\n".join(lines) + "\n"


def write_figure_manifest(repo_root: Path, config: dict[str, Any], jobs: list[dict[str, Any]]) -> Path | None:
    manifest_rel = config.get("deliverables", {}).get("figure_manifest_output")
    if not manifest_rel:
        return None
    manifest_path = (repo_root / manifest_rel).resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(build_figure_manifest(repo_root, config, jobs), encoding="utf-8")
    return manifest_path


def render_one(
    markdown_path: Path,
    html_path: Path,
    css_text: str,
    math_head: str,
    config: dict[str, Any],
    document_language: str,
) -> None:
    html_cfg = config.get("rendering", {}).get("html", {})
    renderer = MarkdownRenderer(
        markdown_path=markdown_path,
        css_text=css_text,
        include_toc=bool(html_cfg.get("include_toc", True)),
        self_contained=bool(html_cfg.get("self_contained", True)),
        math_head=math_head,
        document_language=document_language,
    )
    html_text = renderer.render_document()
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render writing-pipeline markdown outputs into self-contained HTML.")
    parser.add_argument("--config", required=True, help="Path to writing-pipeline run_config.yaml")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    repo_root = config_path.parent.parent.resolve()
    config = load_config(config_path)
    css_text = read_css(repo_root, config)
    math_head = read_math_head(repo_root, config)
    jobs = get_document_jobs(repo_root, config)
    if not jobs:
        raise ValueError("No document jobs found in deliverables configuration.")

    for job in jobs:
        markdown_path = job["markdown_path"]
        html_path = job["html_path"]
        if not markdown_path.is_file():
            if job["required"]:
                raise FileNotFoundError(f"Missing markdown draft: {markdown_path}")
            print(f"Skipping missing optional markdown draft: {markdown_path}")
            continue
        render_one(markdown_path, html_path, css_text, math_head, config, job["language"])
        print(f"Rendered {html_path}")

    manifest_path = write_figure_manifest(repo_root, config, jobs)
    if manifest_path is not None:
        print(f"Updated {manifest_path}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"render_outputs.py failed: {exc}", file=sys.stderr)
        raise

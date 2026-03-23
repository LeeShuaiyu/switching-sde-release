# Outputs Directory

This directory stores both the editable markdown drafts and the rendered deliverables.

Expected files include:

- `report.md`
- `report.zh.md`
- `paper_sections.md`
- `paper_sections.zh.md`
- `report.html`
- `report.zh.html`
- `paper.html`
- `paper.zh.html`
- `figure_manifest.md`

These drafts should be markdown documents with integrated figures or tables when the repository provides suitable visual evidence. Visuals should be introduced, labeled, and interpreted in the prose rather than appended without explanation.

The `assets/` subdirectory should contain every figure cited by the current output drafts. `figure_manifest.md` should map each cited figure to the markdown file and line location where it appears, together with the corresponding output asset path.

`report.html`, `report.zh.html`, `paper.html`, and `paper.zh.html` are the primary human-readable outputs. They should be self-contained documents that embed local figures directly, so a reader can open a single file and view the integrated text and visuals without browsing the asset folder manually. The rendering refresh step should also rebuild `figure_manifest.md` so citation line numbers stay synchronized with the current markdown drafts in all configured languages.

When the runtime layer is used, these files are also validated from `../runs/<run_id>/validation_report.md` to ensure that the publishable workflow contract is satisfied.

If the revision loop ends without a full pass of the final-readiness gate, the files here should still contain the best current draft, while unresolved issues are listed in `../artifacts/final_readiness.md`.

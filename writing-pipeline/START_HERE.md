# Writing Pipeline Entry

This folder defines a reusable, autonomous writing pipeline for turning a messy research repository into:

1. A comprehensive project report grounded in code and results.
2. A paper-ready set of sections written in field-standard or mathematical language rather than code jargon.
3. Figure-rich markdown outputs that integrate repository figures and tables into the written argument whenever suitable visual evidence exists.
4. A figure manifest that records where every cited figure is stored and where it is cited.
5. Self-contained rendered deliverables for human reading, not markdown source alone.
6. Matched English and Chinese versions of the final report and paper outputs.
7. A machine-readable runtime that supports Codex subagent stage claiming, run-state tracking, and validation.

## How Codex should use this folder

When the user asks to "follow the writing pipeline" for the current repository, Codex should:

1. Treat the repository root as the project root unless `run_config.yaml` says otherwise.
2. Read files in this order:
   - `START_HERE.md`
   - `run_config.yaml`
   - `human_notes.md`
   - `workflow.md`
   - the selected style profile in `style_profiles/`
   - the role cards in `roles/` as needed
3. Execute the workflow end to end without asking for routine confirmation.
4. Ask the user only if there is a hard blocker:
   - the repository has no usable results or logs
   - multiple contradictory result sets exist and the best one cannot be identified from evidence
   - the requested claim depends on facts absent from the repository and absent from `human_notes.md`
5. Prefer conservative wording over invention whenever evidence is incomplete.
6. Produce intermediate artifacts in `writing-pipeline/artifacts/` and final outputs in `writing-pipeline/outputs/`.
7. Use the runtime layer in `writing-pipeline/runtime/` and `writing-pipeline/tools/` when the user wants an auditable, subagent-oriented execution.

## Required behavior

- Build a fact-grounded `project_dossier.md` before writing the report.
- Build an `evidence_map.yaml` before making strong claims.
- Build a `terminology_map.md` before outlining so code names can be translated into field-standard terms or explicit mathematical notation.
- Build a `figure_table_plan.md` before drafting so enabled sections have planned visuals or documented exceptions.
- Draft the report before drafting any paper section.
- Draft paper sections from the frozen report plus any explicit human guidance.
- Use one configured language as the canonical drafting language and translate only after that version is frozen.
- Produce both English and Chinese outputs when bilingual mode is enabled, and review them for semantic consistency.
- Copy or normalize every cited figure into `writing-pipeline/outputs/assets/` before finalization so output drafts never depend on external figure paths.
- Emit `writing-pipeline/outputs/figure_manifest.md` so every cited figure has an auditable output location and citation location.
- Treat markdown as the editable source of truth, then render self-contained HTML outputs for final reading and review.
- Render PDF only as an optional enhancement when an external toolchain is available; do not block the workflow on PDF alone.
- Run review loops until the final-readiness gate passes or the configured maximum number of revision rounds is reached.
- If the maximum number of rounds is reached without passing the gate, output the best current draft plus an explicit unresolved-issues list.
- When the runtime layer is enabled, keep stage status in `writing-pipeline/runs/<run_id>/run_state.yaml` and validate the run before calling it publishable.

## Default output files

- `writing-pipeline/artifacts/project_dossier.md`
- `writing-pipeline/artifacts/evidence_map.yaml`
- `writing-pipeline/artifacts/terminology_map.md`
- `writing-pipeline/artifacts/figure_table_plan.md`
- `writing-pipeline/artifacts/report_outline.md`
- `writing-pipeline/artifacts/report_paragraph_plan.md`
- `writing-pipeline/artifacts/report_review_log.md`
- `writing-pipeline/artifacts/paper_outline.md`
- `writing-pipeline/artifacts/paper_paragraph_plan.md`
- `writing-pipeline/artifacts/review_comments.md`
- `writing-pipeline/artifacts/revision_decisions.md`
- `writing-pipeline/artifacts/final_readiness.md`
- `writing-pipeline/outputs/report.md`
- `writing-pipeline/outputs/paper_sections.md`
- `writing-pipeline/outputs/report.zh.md`
- `writing-pipeline/outputs/paper_sections.zh.md`
- `writing-pipeline/outputs/report.html`
- `writing-pipeline/outputs/paper.html`
- `writing-pipeline/outputs/report.zh.html`
- `writing-pipeline/outputs/paper.zh.html`
- `writing-pipeline/outputs/figure_manifest.md`

## Ground rules

- Do not present code variable names as polished academic terminology unless they are already standard in the field.
- Use domain-standard wording or explicit mathematical notation for recurring objects such as trajectories, latent states, switching times, posteriors, and losses.
- Raw code identifiers may appear only in monospace implementation notes, not as the main narrative vocabulary.
- Outputs should be visually integrated rather than text-only when the repository already contains relevant figures or tables.
- Every embedded figure or table should have a caption-like label and explicit interpretation in nearby prose.
- Every figure cited in final outputs should be stored under `writing-pipeline/outputs/assets/`, not only referenced from elsewhere in the repository.
- Final outputs should include a figure manifest describing the citation positions and output asset paths of all cited figures.
- The primary human-readable deliverables should be rendered HTML or PDF, not raw markdown viewed as plain text.
- When bilingual mode is enabled, the translated version must preserve equations, quantitative claims, caveats, and figure/table references from the canonical-language draft.
- Do not overclaim beyond what code, logs, tables, figures, or report evidence can support.
- Do not let reviewer roles directly rewrite the manuscript. Reviewers diagnose; writers and editors revise.
- Keep a clear distinction between:
  - verified facts
  - reasonable inferences
  - unresolved uncertainties

## Rendering command

To refresh the rendered HTML deliverables and the figure manifest after the markdown drafts change, run:

`python3 writing-pipeline/tools/render_outputs.py --config writing-pipeline/run_config.yaml`

## Runtime commands

To initialize and track an auditable Codex-subagent run:

`python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml init --run-id <run_id>`

To sync an initialized run against outputs that already exist on disk:

`python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml sync --run-id <run_id>`

To inspect runnable stages or generate a stage brief for a subagent:

- `python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml next --run-id <run_id>`
- `python3 writing-pipeline/tools/run_workflow.py --config writing-pipeline/run_config.yaml brief --run-id <run_id> --stage <stage_id>`

To validate that the run satisfies the publishable workflow contract:

`python3 writing-pipeline/tools/validate_workflow.py --config writing-pipeline/run_config.yaml --run-id <run_id>`

## If `human_notes.md` is empty

Proceed with defaults from `run_config.yaml` and document the assumptions in the dossier and final-readiness note.

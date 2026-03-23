# Workflow Specification

## Purpose

This workflow turns a newly completed but poorly summarized project repository into a self-contained technical report and then into paper-ready sections. The workflow is designed for autonomous execution with minimal human interruption, but it remains evidence-bound and conservative under uncertainty. The markdown drafts are the source of truth, but the final deliverable to human readers must include rendered, figure-integrated outputs rather than markdown alone. When bilingual output is enabled, one language acts as the canonical drafting language and the second language is produced only after the canonical draft is frozen.

For publishable Codex-subagent use, the workflow must also expose a machine-readable stage registry, a run-state file, per-stage briefs, and a validation report so the execution can be audited after the fact.

## Fact hierarchy

Use evidence in this order of trust:

1. Executable code, checked-in configs, and explicit experiment scripts.
2. Result tables, figures, logs, metrics dumps, and tracked outputs.
3. Readme files, notes, and comments inside the repository.
4. `human_notes.md`.
5. Clearly labeled inference derived from items 1 to 4.

Anything outside this hierarchy must not be treated as fact.

## Stage order

### Stage 0: Repository intake

Owner: `orchestrator`

Actions:

- Discover code, configs, result files, logs, scripts, figures, tables, and notebooks.
- Identify candidate experiment runs and deduplicate repeated outputs.
- Identify likely baselines, evaluation scripts, and environment files.
- Record missing or conflicting materials.

Output:

- Intake notes inside `project_dossier.md`

Exit criteria:

- The repository structure and likely evidence sources are mapped.

### Stage 1: Project dossier extraction

Owners: `dossier_extractor`, `orchestrator`

Actions:

- Reconstruct the project goal.
- Reconstruct the main method and the path that led to the final result.
- Summarize the best available results and how they were obtained.
- Extract detours, failed attempts, or tuning paths that reveal challenges.
- List baselines, tests, environments, hyperparameters, and architecture details.
- Mark uncertain facts explicitly.

Required dossier sections:

- Project objective
- Problem setting
- Main method
- Final results
- Result provenance
- Baselines and comparisons
- Tests and ablations
- Environment and dependencies
- Hyperparameters
- Model architecture
- Training and inference procedure
- Challenges and detours
- Open uncertainties

Output:

- `artifacts/project_dossier.md`

Exit criteria:

- Every required dossier section is present.
- Every nontrivial factual statement is either supported or marked uncertain.

### Stage 2: Evidence map

Owners: `evidence_mapper`, `fact_consistency_reviewer`

Actions:

- Create a claim-to-evidence mapping for all strong claims needed by the report.
- Record file paths and, when possible, line numbers or table/figure identifiers.
- Flag unsupported claims before drafting.

Output:

- `artifacts/evidence_map.yaml`

Exit criteria:

- Strong claims needed for the report have evidence entries or explicit "unsupported" status.

### Stage 2A: Terminology and notation map

Owners: `terminology_mapper`, `global_editor`

Actions:

- Extract recurring code labels, private method names, dataset aliases, and implementation shorthand that would leak into prose.
- Map each item to a preferred domain term, standard label, or explicit mathematical symbol.
- Define first-use notation for the core objects that recur across the report and paper.
- Mark banned raw identifiers and document any unavoidable implementation-only names that must remain monospaced.

Output:

- `artifacts/terminology_map.md`

Exit criteria:

- Every recurring technical object has an approved prose term or notation.
- No unresolved code-style label remains untracked before drafting starts.

### Stage 2B: Figure and table plan

Owners: `figure_curator`, `outliner`

Actions:

- Inventory reusable figures and tables from the repository, preferring final checked-in assets over exploratory ones.
- For each selected visual, record the supporting claim, target section, target paragraph, and caption intent.
- Assign each selected figure a neutral output filename under `outputs/assets/` so final drafts do not depend on raw repository figure paths.
- Require a visual or documented exception for every enabled section whose evidence materially benefits from a figure or table.

Output:

- `artifacts/figure_table_plan.md`

Exit criteria:

- Enabled sections have planned visuals or explicit exceptions.
- Every selected visual is tied to a concrete claim rather than decorative inclusion.

### Stage 3: Report outline

Owners: `outliner`, `orchestrator`

Actions:

- Use the dossier, evidence map, terminology map, figure plan, and configuration to produce a section outline.
- Select section order and coverage based on the configured audience and report scope.
- Define what each section must accomplish.
- Define which visuals and notation decisions belong in each section.
- Ensure the enabled sections read as one document rather than as disconnected chapter stubs.

Output:

- `artifacts/report_outline.md`

Exit criteria:

- Every required report topic is assigned to a section.
- Section purposes are explicit and non-overlapping.

### Stage 4: Report paragraph plan

Owners: `outliner`, `global_editor`

Actions:

- Expand the outline into a paragraph-level plan.
- Respect any configured section paragraph budget unless evidence coverage requires a documented adjustment.
- For each paragraph define:
  - purpose
  - target evidence
  - terminology or notation anchor
  - visual anchor or explicit no-visual exception
  - target length
  - connection to adjacent paragraphs
  - content that must not be repeated elsewhere

Output:

- `artifacts/report_paragraph_plan.md`

Exit criteria:

- Every planned paragraph has a clear role and evidence anchor.

### Stage 5: Report drafting

Owners: `paragraph_writer`, `local_reviewer`

Actions:

- Draft the report paragraph by paragraph from the paragraph plan.
- Enforce the approved terminology map and use mathematical notation for core objects when it improves clarity.
- Replace ad hoc code labels with accepted domain terms rather than private project jargon.
- Include a method section whenever the configuration enables it, and make the method understandable without requiring the reader to inspect code.
- Define every scenario label, benchmark split, acronym, and metric on first use.
- Embed planned figures and tables in markdown when available, and interpret them in nearby prose.
- Ensure every embedded figure path resolves inside `outputs/assets/` rather than to an external repository location.
- Preserve enough technical detail to make the report useful as a paper source.
- Remove repository-relative narration such as "in this repo" or "the workspace" unless the sentence is explicitly about artifact provenance rather than the scientific content.

Output:

- `outputs/report.md`

Exit criteria:

- All planned report paragraphs are drafted.

### Stage 6: Report review and freeze

Owners: `local_reviewer`, `logic_reviewer`, `outline_compliance_reviewer`, `fact_consistency_reviewer`, `global_editor`

Actions:

- Run style, readability, terminology, and notation review.
- Run cross-section logic and repetition review.
- Run outline-compliance review.
- Run code-and-result consistency review.
- Run figure/table integration review.
- Verify that every figure cited by the report exists under `outputs/assets/` and that no embedded figure points outside the output directory.
- Verify that the report markdown is renderable into a self-contained human-readable artifact without broken figures.
- Run self-containment review from the perspective of a reader who has never seen the repository.
- Apply accepted fixes and freeze the report for paper drafting.

Outputs:

- `artifacts/report_review_log.md`
- updated `outputs/report.md`

Exit criteria:

- No high-severity factual errors remain.
- No major outline violations remain.
- The report is coherent enough to act as the single paper source of truth.

### Stage 6A: Report translation and bilingual consistency review

Owners: `translator`, `bilingual_consistency_reviewer`, `global_editor`

Actions:

- Translate the frozen canonical-language report into each configured secondary language.
- Preserve claims, numbers, units, equations, figure references, table references, and section structure unless the configuration explicitly permits localized restructuring.
- Keep mathematical notation invariant across languages unless a notation explanation requires a local-language gloss.
- Review the bilingual pair for drift in claim strength, unsupported additions, missing caveats, and mismatched figure or table references.
- Apply accepted consistency fixes without weakening the canonical evidence base.

Outputs:

- translated report markdown outputs such as `outputs/report.zh.md`
- bilingual consistency notes in `artifacts/report_review_log.md`

Exit criteria:

- Configured report languages are all present.
- Cross-language review finds no high-severity semantic drift.

### Stage 7: Paper outline

Owners: `outliner`, `advisor`

Actions:

- Use the frozen report, terminology map, figure plan, and `human_notes.md` to define the paper section scope.
- Respect the selected style profile.
- Support these optional section types based on configuration:
  - experiment section
  - introduction
  - method section
  - symbol or notation section
  - problem formalization section

Outputs:

- `artifacts/paper_outline.md`

Exit criteria:

- The paper outline matches the configured scope and target style.

### Stage 8: Paper paragraph plan and drafting

Owners: `outliner`, `paragraph_writer`, `global_editor`

Actions:

- Produce paragraph-level plans for the enabled paper sections.
- Respect the configured section paragraph budget and target style.
- For each paragraph specify purpose, evidence source, target length, rhetorical role, notation needs, and visual placement.
- Draft the paper sections from the plan and the frozen report.
- Make the enabled sections form a coherent paper fragment that a new reader can follow from problem statement through method to empirical evidence.
- Embed planned figures or tables in markdown and interpret them as part of the argument rather than as detached decoration.
- Ensure every embedded paper figure also resolves inside `outputs/assets/`.

Outputs:

- `artifacts/paper_paragraph_plan.md`
- `outputs/paper_sections.md`

Exit criteria:

- All enabled paper paragraphs are drafted.

### Stage 9: Review cycle

Owners: `local_reviewer`, `logic_reviewer`, `outline_compliance_reviewer`, `fact_consistency_reviewer`, `advisor`, `reviewer`, `revision_arbiter`, `global_editor`

Actions:

- Review the paper draft for style, terminology, notation, visuals, logic, structure, and consistency with the report.
- Review whether every benchmark name, scenario label, method family, and metric is understandable without repository context.
- Review whether every cited figure is present in `outputs/assets/` and whether the set of cited figures is recorded in the output figure manifest.
- Review whether the frozen markdown drafts can be rendered into self-contained HTML without figure loss or layout breakage.
- Run advisor review for contribution emphasis and narrative shape.
- Run reviewer review for skeptical peer-review criticism.
- Aggregate comments with severity labels.
- Use the arbiter to classify each comment:
  - adopt
  - partially adopt
  - reject
  - defer
- Revise only from accepted decisions.

Outputs:

- `artifacts/review_comments.md`
- `artifacts/revision_decisions.md`
- updated `outputs/paper_sections.md`

Exit criteria:

- The configured final-readiness gate passes, or
- the maximum number of revision rounds is reached

### Stage 9A: Paper translation and bilingual consistency review

Owners: `translator`, `bilingual_consistency_reviewer`, `global_editor`

Actions:

- Translate the frozen canonical-language paper draft into each configured secondary language.
- Preserve claims, equations, numbers, figures, tables, and caveats across languages.
- Check that localized prose does not invent stronger novelty, softer limitations, or different benchmark interpretations.
- Verify that every figure and table reference still points to the same underlying asset and evidence in each language version.

Outputs:

- translated paper markdown outputs such as `outputs/paper_sections.zh.md`
- bilingual review notes inside `artifacts/review_comments.md` or `artifacts/report_review_log.md`

Exit criteria:

- Configured paper languages are all present.
- Cross-language review finds no high-severity semantic drift.

### Stage 10: Finalization

Owner: `orchestrator`

Actions:

- Write the final readiness memo.
- State whether the current paper draft is final, near-final, or best-effort pending human input.
- Write `outputs/figure_manifest.md`, mapping every cited figure to the output file, citation position, caption position, and output asset path.
- Render self-contained HTML deliverables from the final markdown drafts so the workflow produces human-readable outputs with inline figures rather than markdown source alone.
- If an external PDF toolchain is available and configured, render PDF versions as an optional distribution format.
- Update the runtime validation report for the current run.
- If unresolved issues remain, list them explicitly.

Output:

- `artifacts/final_readiness.md`
- `outputs/figure_manifest.md`
- `outputs/report.html`
- `outputs/paper.html`
- `outputs/report.zh.md`
- `outputs/paper_sections.zh.md`
- `outputs/report.zh.html`
- `outputs/paper.zh.html`
- optional `outputs/report.pdf`
- optional `outputs/paper.pdf`
- `runs/<run_id>/validation_report.md`

## Review severities

- `high`: factually wrong, unsupported, self-contradictory, or likely to mislead reviewers
- `medium`: important but nonfatal logic, clarity, repetition, or scope issue
- `low`: phrasing, rhythm, local polish, or optional style improvement

## Revision arbitration rules

The arbiter should prefer:

1. Truth over elegance.
2. Evidence-backed caution over flashy but unsupported claims.
3. Venue-fit writing over generic academic prose.
4. Deleting redundant text over preserving all drafted material.

The arbiter should reject comments that:

- demand unsupported claims
- require facts absent from evidence
- push the draft outside the configured scope
- sacrifice technical correctness for rhetoric

## Final-readiness gate

The draft is ready to stop only when all are true:

- No unresolved `high` severity factual issues remain.
- No unresolved `high` severity outline-compliance issues remain.
- No unresolved `high` severity report-consistency issues remain.
- Terminology follows the approved terminology map and no raw code-internal naming leaks into narrative prose.
- The draft includes an explicit method section if the configuration requires it.
- Core mathematical objects are named or symbolized consistently.
- A reader who has not seen the repository can understand the problem setting, method, scenario definitions, and metrics without external lookup.
- Benchmark labels and scenario labels are accompanied by semantic explanations, not only by shorthand names.
- Enabled sections satisfy the configured visual minimums or record explicit exceptions.
- Every embedded figure or table has a caption-like label and explicit interpretation in nearby prose.
- Every embedded figure resolves to a file stored under `outputs/assets/`.
- `outputs/figure_manifest.md` exists and covers every cited figure in the final drafts.
- `outputs/report.html` and `outputs/paper.html` exist as human-readable rendered deliverables.
- Configured secondary-language markdown and HTML outputs exist.
- Cross-language review confirms that claims, numbers, math, and figure/table references remain aligned across languages.
- Rendered HTML outputs are self-contained and do not depend on external image paths at reading time.
- The runtime validation report exists for the current run and reports no blocking errors.
- Repetition across enabled sections is controlled.
- Two consecutive review rounds introduce no new major issue, unless the configured maximum rounds is one.

If the gate does not pass by the configured maximum number of revision rounds:

- stop the loop
- keep the best current draft
- document remaining issues in `final_readiness.md`

## Hard-block policy

Pause for user input only when:

- no credible final result can be identified
- multiple result sets conflict and evidence cannot rank them
- the requested paper emphasis depends on a strategic choice not recoverable from code or notes

Otherwise proceed autonomously and record assumptions.

# Subagent Workflow Run

## Purpose

This note records a demonstrative workflow pass executed with multiple subagents rather than with a single serial writer. The goal was to show how the role cards can be instantiated as bounded parallel tasks and then reintegrated by the orchestrator.

## Subagents Used

| Role | Owned file(s) | Result |
|---|---|---|
| dossier_extractor | `writing-pipeline/artifacts/project_dossier.md` | Refreshed the project objective, benchmark structure, method summary, hyperparameters, tests, ablations, and uncertainty list from repository evidence. |
| evidence_mapper | `writing-pipeline/artifacts/evidence_map.yaml` | Rebuilt the claim-to-evidence table as 12 directly reusable records with concrete `source_path` and `locator` fields. |
| figure_curator | `writing-pipeline/artifacts/figure_table_plan.md` | Reframed the visual plan around the current neutralized output assets and the rendered output files rather than raw legacy report paths alone. |
| reviewer | `writing-pipeline/artifacts/review_comments.md` | Produced a stricter peer-review style diagnosis focused on fairness of comparison, collapse-threshold provenance, seed-average limitations, and nonlinear figure linkage. |

## Main-Thread Integration

After the subagents returned, the orchestrator applied the actionable review findings to the final outputs:

- clarified that the controlled nominal linear comparison is the transformer block, while the stronger LSTM row reflects family-level headroom rather than a head-only gain
- clarified that the collapse thresholds are inherited from the released benchmark scripts
- disclosed that the released public tables report three-seed averages without confidence intervals
- strengthened the nonlinear figure-to-text linkage
- recorded the decisions in `revision_decisions.md` and `report_review_log.md`

## Effect on the Workflow

The practical effect of the subagent pass is that the workflow now has:

- a sharper dossier
- a more directly reusable evidence map
- a figure plan aligned with the actual output assets and HTML deliverables
- a more realistic reviewer pass than the earlier generic comments
- manuscript text updated in response to those review findings

## Files Touched in This Run

- `writing-pipeline/artifacts/project_dossier.md`
- `writing-pipeline/artifacts/evidence_map.yaml`
- `writing-pipeline/artifacts/figure_table_plan.md`
- `writing-pipeline/artifacts/review_comments.md`
- `writing-pipeline/artifacts/revision_decisions.md`
- `writing-pipeline/artifacts/report_review_log.md`
- `writing-pipeline/artifacts/final_readiness.md`
- `writing-pipeline/outputs/report.md`
- `writing-pipeline/outputs/paper_sections.md`

## Remaining Boundaries

- This run reused existing repository evidence and did not retrain models or rerun benchmarks.
- PDF is still optional because no external PDF toolchain is configured in the current environment.
- The role cards are now demonstrated in practice, but the workflow is still orchestrated by Codex rather than by a repository-native multi-agent runtime.

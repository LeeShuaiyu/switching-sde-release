# Artifacts Directory

This directory stores intermediate, inspectable outputs created by the pipeline.

Expected files include:

- `project_dossier.md`
- `evidence_map.yaml`
- `terminology_map.md`
- `figure_table_plan.md`
- `report_outline.md`
- `report_paragraph_plan.md`
- `report_review_log.md`
- `paper_outline.md`
- `paper_paragraph_plan.md`
- `review_comments.md`
- `revision_decisions.md`
- `final_readiness.md`

These files should remain more structured and diagnostic than the final outputs.

Run-scoped state and validation records do not live here. They are stored under `../runs/<run_id>/` so the workflow can be audited without mixing runtime metadata into the manuscript artifacts.

# Role Card: Translator

## Mission

Translate the frozen canonical-language draft into the configured secondary language without changing the scientific meaning.

## Inputs

- frozen canonical-language report or paper draft
- `run_config.yaml`
- `terminology_map.md`
- `evidence_map.yaml`
- `figure_table_plan.md`

## Outputs

- translated markdown draft such as `outputs/report.zh.md` or `outputs/paper_sections.zh.md`

## Must preserve

- claims and caveats
- numbers, units, and thresholds
- mathematical notation
- figure and table references
- section ordering unless the workflow explicitly allows localized restructuring

## Must not do

- strengthen novelty or significance in translation
- weaken limitations or uncertainty markers
- rename figures, tables, or equations in a way that breaks alignment with the source draft


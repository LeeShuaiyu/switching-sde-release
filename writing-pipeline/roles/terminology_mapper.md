# Role Card: Terminology Mapper

## Mission

Translate repository-specific code labels into field-standard prose terms and explicit mathematical notation before drafting starts.

## Inputs

- `artifacts/project_dossier.md`
- repository code and configs
- selected style profile
- `human_notes.md`

## Outputs

- `artifacts/terminology_map.md`

## For each recurring concept

- record the raw repository label if one exists
- record the preferred prose term
- record the preferred mathematical symbol when useful
- state whether the raw label is banned in narrative prose
- add a short note if the mapping is uncertain

## Quality standard

- The map should let a writer avoid code jargon without inventing fake theory language.
- Core objects should have stable first-use notation across report and paper outputs.

## Must not do

- Invent nonstandard mathematical notation when plain domain language is clearer.
- Treat internal model nicknames as polished scientific terminology.

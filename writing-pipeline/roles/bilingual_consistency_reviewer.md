# Role Card: Bilingual Consistency Reviewer

## Mission

Check that the bilingual outputs say the same thing scientifically, not merely that they read fluently in two languages.

## Inputs

- canonical-language markdown draft
- translated markdown draft
- `evidence_map.yaml`
- `terminology_map.md`

## Outputs

- consistency comments grouped by severity

## Check for

- drift in claim strength
- mismatched numbers, units, thresholds, or seed counts
- altered mathematical notation
- missing limitations or caveats in one language
- mismatched figure or table references
- untranslated code identifiers leaking into polished prose

## Must not do

- rewrite the drafts directly
- approve stylistic paraphrase if it changes scientific meaning

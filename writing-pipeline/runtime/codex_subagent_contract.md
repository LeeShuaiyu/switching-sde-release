# Codex Subagent Contract

A Codex subagent executing one workflow stage must follow these rules.

## Ownership

- Only edit the files listed in the stage write scope.
- Treat sibling stage outputs as owned by other agents unless the orchestrator explicitly reassigns them.
- Do not revert changes made by other agents.

## Evidence discipline

- Read the declared inputs before writing.
- Do not invent claims that are unsupported by repository evidence.
- Record uncertainties instead of silently guessing.

## Handoff discipline

- Leave the stage outputs in a readable, reviewable state.
- Add concise notes when assumptions, blockers, or unresolved risks remain.
- Do not mark a stage complete unless every required output for that stage exists.

## Manuscript discipline

- Reviewers diagnose but do not directly rewrite final manuscript sections unless the stage write scope explicitly includes those files.
- Translators preserve claims, math, numbers, figure references, and caveats.
- Editors integrate accepted changes without introducing new unsupported claims.

## Collaboration discipline

- You are not alone in the codebase.
- Assume other agents may be modifying neighboring files.
- Prefer narrow, stage-bounded edits that are easy for the orchestrator to validate and merge.

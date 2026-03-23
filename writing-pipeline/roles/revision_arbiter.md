# Role Card: Revision Arbiter

## Mission

Decide how review comments should affect the next draft and when the process should stop.

## Inputs

- review comments
- current draft
- evidence map
- selected style profile
- `run_config.yaml`

## Outputs

- `artifacts/revision_decisions.md`
- stop or continue decision

## Decision classes

- `adopt`
- `partially_adopt`
- `reject`
- `defer`

## Decision criteria

- Does the comment improve truthfulness?
- Does the comment improve acceptance probability without sacrificing accuracy?
- Is the requested change supported by evidence?
- Is the comment inside the configured scope?
- Is the issue already addressed elsewhere?
- Does the comment improve terminology discipline or visual communication without weakening accuracy?

## Stop rules

- Stop when the final-readiness gate passes.
- Stop when the maximum number of revision rounds is reached.
- If stopping without passing the gate, require an unresolved-issues list.

## Must not do

- Accept comments that force unsupported claims.
- Continue the loop indefinitely.

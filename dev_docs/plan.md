# Current Plan

> Update this at the start of any non-trivial task. Strike through
> items as they complete; archive completed plans by moving the
> section to `dev_docs/changelog.md` and resetting this file.

## Active

_No active task. Waiting for user direction._

## Backlog (high level)

See `dev_docs/ideas.md` for the open backlog with stable IDs. The
plan file references those IDs once they become active work.

## How to use this file

1. When the user assigns a task, write a short "Goal" + "Acceptance"
   block at the top of the **Active** section.
2. Break into phases. Each phase is a checkbox list with files
   touched, commands to run, and a verification step.
3. As phases complete, check them off. Keep notes in the same phase
   block (timing surprises, scope changes, things deferred).
4. When the task is fully done, move the whole block into
   `dev_docs/changelog.md` under today's date and clear it from here.

## Template

```markdown
## Active

### Goal
<one-sentence goal>

### Acceptance
- [ ] <observable criterion 1>
- [ ] <observable criterion 2>

### Phase 1 — <name>
- [ ] <step>
- [ ] Verification: <command + expected output>

### Phase 2 — <name>
- [ ] ...
```

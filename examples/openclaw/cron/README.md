# OpenClaw Cron Layout

This example shows the recommended task-based scheduling model for one book team.

For the full operator procedure, use:

- [OpenClaw operations runbook](../../../docs/openclaw-operations-runbook.md)
- [OpenClaw operations runbook (Chinese)](../../../docs/openclaw-operations-runbook.zh-CN.md)

Install the skill first:

```bash
clawhub install mumuai-novel-skills
```

Then configure one logical job set per book:

- `showrunner-scan`
- `writer-run`
- `editor-run`
- `reader-panel-run`

Each job should reuse the same:

- `MUMU_API_URL`
- `MUMU_USERNAME`
- `MUMU_PASSWORD`
- `PROJECT_ID`
- optional `STYLE_ID`

Each job should use a different `MUMU_OWNER_ID`.

Example owner naming:

- `book-a-showrunner`
- `book-a-writer`
- `book-a-chief-editor`
- `book-a-reader-panel`

## Recommended Responsibilities

### `showrunner-scan`

- cadence: every 30 minutes
- responsibility:
  - inspect book state
  - decide `continue`, `slow_down`, or `pause_and_fix`
  - wake the next task-specific role

### `writer-run`

- responsibility:
  - expand outline runway
  - generate more chapters only when the book is healthy enough to continue

### `editor-run`

- responsibility:
  - fetch unaudited chapters
  - analyze quality and continuity
  - approve or rewrite

### `reader-panel-run`

- responsibility:
  - provide user-side evaluation
  - report whether current serialization should keep its pace

## Suggested Guardrails

- Do not schedule blind auto-publication.
- Do not let `Writer` and `Chief Editor` act on the same chapter at the same time.
- Do not reuse `MUMU_OWNER_ID` across jobs.
- Treat one book as one team and one scheduling unit.

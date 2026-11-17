---
name: changelog-tracking
description: >-
  Procedures and standards for logging every code change, file creation, modification, refactoring, and test execution into testing/changelogs.md with precise timestamps, detailed detection of changes, and exact file paths. Use this skill whenever creating, modifying, deleting, or testing files across the repository.
---

# Changelog Tracking & Change Audit Skill

This skill enforces continuous documentation of all project changes in [`testing/changelogs.md`](../../testing/changelogs.md). Maintaining an accurate audit trail of changes ensures accountability, traceability, easier debugging, and transparent progression across both backend and frontend development.

---

## 1. Core Rule: Habitual Documentation

Whenever any file is created, modified, refactored, or deleted, or when significant configuration, test, or environment setups take place:
1. Identify the exact file path(s) touched.
2. Summarize what was added, changed, or removed (change detection).
3. Log an entry at the top of the log section in `testing/changelogs.md` with the current local timestamp (`YYYY-MM-DD HH:MM:SS [Timezone]`).

---

## 2. Standard Changelog Entry Format

Every entry in `testing/changelogs.md` must follow this structure:

```markdown
### [<Timestamp>] - <Concise Title of Change>
- **Type**: `Feature` | `Bugfix` | `Refactor` | `Config` | `Test` | `Documentation` | `Skill`
- **Description / Detection of Changes**:
  - Detailed bullet points describing specifically what was introduced, updated, or removed.
  - Reason for the change or error addressed.
- **Affected Files**:
  - `[CREATED]` `relative/path/to/file` - brief summary of purpose
  - `[MODIFIED]` `relative/path/to/file` - specific changes made (e.g., lines or components touched)
  - `[DELETED]` `relative/path/to/file` - reason for removal
- **Verification / Test Result**:
  - Command run (e.g., `pytest`, `npm run build`, `python -c ...`) and outcome (e.g., `Build succeeded`, `All tests passed`).
```

---

## 3. Best Practices

- **Atomic Logging**: Group related file changes belonging to the same task or feature together under a single cohesive timestamp entry.
- **Explicit File Paths**: Always list full relative file paths from repository root so they can be easily located or linked.
- **Diff / Change Detection Clarity**: Do not just say "updated file". Clearly state what logic was altered, what models or endpoints were added, or what styles were updated.
- **Preserve History**: Append new entries to the changelog in reverse chronological order (newest on top) or sequential order, maintaining clean Markdown formatting.

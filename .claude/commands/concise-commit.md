# concise-commit

Generate a single-line Conventional Commit message for the staged diff.

Rules:
- Format: `type(scope): summary` (<= 72 chars).
- No body, no bullet list, no trailing notes.
- Imperative mood; describe the change, not the process.

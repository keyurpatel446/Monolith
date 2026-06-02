# monolith.implement

Implement the feature by executing its tasks in dependency order.

Pre-flight (read ALL of these before writing any code):
- `specs/<feature>/spec.md` — requirements and acceptance criteria.
- `specs/<feature>/plan.md` — architecture and component design.
- `specs/<feature>/tasks.md` or `TASKS.md` — ordered task list.
- `.monolith/memory/constitution.md` — non-negotiable principles.

Execution rules:
- Work tasks in dependency order (`@after:` deps must be done first).
- Mark each task `doing` before starting, `done` when tests pass.
- Run `monolith run -- <test-cmd>` after each task to catch regressions.
- If a task is blocked or unclear, stop and ask — do not guess.
- After all tasks: run `monolith analyze <feature>` to confirm alignment.

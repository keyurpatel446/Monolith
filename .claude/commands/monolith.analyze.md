# monolith.analyze

Check that spec, plan, and tasks are internally consistent for a feature.

Steps:
1. Ask: which feature? (or infer from context)
2. Read `specs/<feature>/spec.md`, `plan.md`, `tasks.md`.
3. For each requirement in spec.md — is it addressed in plan.md?
4. For each plan component — does a task exist for it?
5. For each acceptance criterion — is there a task that satisfies it?
6. Report findings in three groups:
   COVERED:  requirement → plan section → task id
   GAP:      requirement with no plan or task coverage
   ORPHAN:   tasks or plan sections with no spec backing
7. If gaps exist, ask the user whether to fix spec, plan, or tasks.

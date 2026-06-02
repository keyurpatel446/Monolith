# monolith.clarify

Read the feature spec and surface every ambiguity that would block a correct plan.

Steps:
1. Ask: which feature? (or infer from context)
2. Read `specs/<feature>/spec.md`.
3. List every open question, ambiguity, or underspecified requirement.
   Format: `Q1: <question>` — one per line, no filler.
4. Wait for the user to answer each question.
5. Update `specs/<feature>/spec.md` with the resolved answers.
6. Confirm: 'Spec updated. Ready to plan.'

Do NOT start planning until all blockers are resolved.

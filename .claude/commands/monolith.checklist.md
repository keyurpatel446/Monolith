# monolith.checklist

Generate a quality checklist and confirm the feature is ready to ship.

Steps:
1. Ask: which feature? (or infer from context)
2. Read `specs/<feature>/spec.md` and `plan.md`.
3. Generate a checklist with four sections:
   Spec compliance   — one checkbox per acceptance criterion from spec.md.
   Implementation    — tests, lint, type-check, no TODOs.
   Cross-artifact    — spec ↔ plan ↔ tasks consistent.
   Review            — PR description, reviewer sign-off, CHANGELOG.
4. Print the checklist. Work through each unchecked item with the user.
5. Only declare 'Ready to ship' when every box is checked.

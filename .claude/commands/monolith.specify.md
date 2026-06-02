# monolith.specify

Create `specs/<feature>/spec.md` for the feature the user names.

Steps:
1. Ask: what is the feature name? (or infer from context)
2. Read `.monolith/memory/constitution.md` if it exists.
3. Read any existing `specs/<feature>/spec.md`.
4. Fill in or update the spec with all of:
   - Problem Statement (one paragraph)
   - Goals (bullet list — what must be true when done)
   - Non-Goals (what we are NOT building)
   - User Stories (As a <role>, I want <action> so that <outcome>)
   - Functional Requirements (numbered, specific, testable)
   - Acceptance Criteria (checkbox list)
   - Open Questions (anything unresolved)
5. Stop. Do NOT plan or implement.

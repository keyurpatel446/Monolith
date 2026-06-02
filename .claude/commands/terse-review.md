# terse-review

Review the current diff for correctness bugs only.

Output:
- One finding per line: `file:line - issue`.
- No praise, no summary, no style nitpicks unless they cause bugs.
- If nothing is wrong, reply exactly: `No correctness issues found.`

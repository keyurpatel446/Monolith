"""Canonical token-efficiency ruleset.

These rules are authored once here and compiled into every agent's native
config by the adapters. Each rule has a stable id (so profiles can select a
subset) and a single-sentence directive written in the imperative.

The directives synthesize the proven techniques from the projects Monolith
draws on: stripping conversational filler (claude-token-efficient) and
favouring dense, low-token output (caveman).
"""

# id -> directive text
RULES = {
    "no_openers": (
        "Do not open with greetings, acknowledgements, or filler such as "
        '"Sure!", "Great question!", or "Certainly".'
    ),
    "no_closers": (
        "Do not end with pleasantries or offers of further help such as "
        '"I hope this helps!" or "Let me know if you need anything else."'
    ),
    "no_restate": (
        "Do not restate or paraphrase the request before answering."
    ),
    "lead_with_answer": (
        "Lead with the answer or the result; put caveats and context after, "
        "only if they matter."
    ),
    "no_unsolicited_summary": (
        "Do not append a summary of what you just did unless explicitly asked."
    ),
    "dense_format": (
        "Prefer dense formats: tables, lists, and code blocks over prose when "
        "they convey the same information in fewer tokens."
    ),
    "no_code_narration": (
        "Do not narrate or re-explain code you just wrote unless asked; let "
        "the code and concise comments speak."
    ),
    "minimal_comments": (
        "Write only comments that add non-obvious information; skip comments "
        "that merely restate the code."
    ),
    "no_overengineering": (
        "Implement what was asked. Do not add speculative abstractions, "
        "options, or defensive code that was not requested."
    ),
    "no_sycophancy": (
        "Do not agree reflexively. If something is wrong or a better option "
        "exists, say so plainly and briefly."
    ),
    "no_repeat_apology": (
        "Correct mistakes in one short sentence; do not apologize repeatedly."
    ),
    "terse_prose": (
        "Keep prose telegraphic: short sentences, no adverbs of emphasis, no "
        "marketing tone. Cut any word that does not change the meaning."
    ),
    "bullets_over_paragraphs": (
        "Default to bullet points over paragraphs; use at most one short "
        "paragraph per idea."
    ),
}

# The single rule that must always be present so user intent is never lost.
OVERRIDE_NOTE = "User instructions in the conversation always override these rules."


def get_rule(rule_id):
    """Return the directive text for a rule id, or None if unknown."""
    return RULES.get(rule_id)


def known_rule_ids():
    """Return the set of all built-in rule ids."""
    return set(RULES.keys())

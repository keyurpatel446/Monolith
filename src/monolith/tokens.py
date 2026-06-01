"""Token counting.

Monolith reports two kinds of numbers: *projected* reductions (from the tier
definitions) and *measured* reductions (from the benchmark harness). Measured
numbers need an actual token count, which this module provides.

Counting strategy
-----------------
* If the optional ``tiktoken`` package is installed we use it for an exact
  count against the ``cl100k_base`` encoding (used by recent OpenAI/Anthropic
  tokenizers and a good general proxy).
* Otherwise we fall back to a fast heuristic (~4 characters per token).

Reductions are reported as *ratios* (1 - optimized/baseline). Ratios are far
less sensitive to the absolute counter than raw token totals are, so the
heuristic is perfectly adequate for comparing two texts — and we always report
which counter produced the numbers via :func:`counter_name`.
"""

from __future__ import annotations

# tiktoken is optional. Import lazily-tolerant so the core stays dependency-free.
try:  # pragma: no cover - exercised only when the extra is installed
    import tiktoken
except Exception:  # ImportError, or a broken install
    tiktoken = None

_HEURISTIC_CHARS_PER_TOKEN = 4
_ENCODING_NAME = "cl100k_base"

# Cache the encoding object; building it is relatively expensive.
_encoding = None


def _heuristic_count(text: str) -> int:
    """Estimate tokens as roughly one per four characters."""
    return max(0, round(len(text) / _HEURISTIC_CHARS_PER_TOKEN))


def _get_encoding():
    """Return a cached tiktoken encoding, or ``None`` if unavailable."""
    global _encoding
    if tiktoken is None:
        return None
    if _encoding is None:
        try:
            _encoding = tiktoken.get_encoding(_ENCODING_NAME)
        except Exception:  # pragma: no cover - network/registry failure
            return None
    return _encoding


def count_tokens(text: str) -> int:
    """Return the token count for ``text`` (exact if tiktoken is present)."""
    enc = _get_encoding()
    if enc is not None:
        return len(enc.encode(text))
    return _heuristic_count(text)


def counter_name() -> str:
    """Return a label identifying which counter is active.

    Useful so recorded results note how they were measured, e.g.
    ``"tiktoken:cl100k_base"`` or ``"heuristic:4cpt"``.
    """
    if _get_encoding() is not None:
        return f"tiktoken:{_ENCODING_NAME}"
    return "heuristic:4cpt"

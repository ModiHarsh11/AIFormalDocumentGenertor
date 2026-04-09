"""Post-processing: markdown stripping, header-leakage removal, structural checks.

All functions in this module are intentionally *destructive* — they strip
formatting characters globally.  This is acceptable for government document
bodies which should never contain markdown, but be aware this is lossy
if the domain changes.
"""

import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Markdown stripping
# ---------------------------------------------------------------------------

# Pre-compiled patterns (avoid recompilation per call)
_RE_CODE_BLOCK = re.compile(r"```[\s\S]*?```")
_RE_BOLD_ITALIC = re.compile(r"\*+")
_RE_UNDERSCORE_ITALIC = re.compile(r"(?<!\w)_([^_]+)_(?!\w)")
_RE_BULLET_STRIP = re.compile(r"^[-•]\s*", re.MULTILINE)
_RE_NUMBERED_STRIP = re.compile(r"^\d+\.\s*", re.MULTILINE)
_RE_HEADINGS = re.compile(r"#+\s*")
_RE_DOUBLE_SPACES = re.compile(r" {2,}")


def strip_markdown(text: str) -> str:
    """Remove common markdown artifacts from LLM output.

    .. warning::
        Literal ``*`` and ``_`` characters in legitimate content will be removed.
    """
    text = _RE_CODE_BLOCK.sub("", text)
    text = _RE_BOLD_ITALIC.sub("", text)
    text = _RE_UNDERSCORE_ITALIC.sub(r"\1", text)
    text = _RE_BULLET_STRIP.sub("", text)
    text = _RE_NUMBERED_STRIP.sub("", text)
    text = _RE_HEADINGS.sub("", text)
    text = _RE_DOUBLE_SPACES.sub(" ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Header-leakage detection
# ---------------------------------------------------------------------------
# Covers English and Hindi header leakage from the LLM across all document types.

_LEAKAGE_PATTERNS = re.compile(
    r"^("
    # English headers (shared)
    r"Subject|Ref|Reference|Date|From|To|Signature"
    r"|"
    # English headers (document-type specific)
    r"Office Order|Circular|Policy"
    r"|"
    # Hindi headers (shared: विषय = Subject, संदर्भ = Reference, दिनांक = Date,
    #  प्रेषक = From, प्राप्तकर्ता = To, हस्ताक्षर = Signature)
    r"विषय|संदर्भ|दिनांक|प्रेषक|प्राप्तकर्ता|हस्ताक्षर"
    r"|"
    # Hindi headers (document-type specific: कार्यालय आदेश = Office Order,
    #  परिपत्र = Circular, नीति = Policy)
    r"कार्यालय आदेश|परिपत्र|नीति"
    r")\s*[:—–-].*$",
    re.MULTILINE | re.IGNORECASE,
)


def validate_body(text: str) -> str:
    """Strip header/metadata lines the LLM should not have included."""
    cleaned, count = _LEAKAGE_PATTERNS.subn("", text)
    if count:
        logger.warning(
            "LLM output contained %d leaked header line(s) — stripped automatically.",
            count,
        )
    cleaned = cleaned.strip()
    _check_structure(cleaned)
    return cleaned


# ---------------------------------------------------------------------------
# Structural checks (soft / non-blocking)
# ---------------------------------------------------------------------------
# These log warnings when LLM output violates prompt rules but do NOT reject
# the output.  Production monitoring can alert on repeated violations.

_BULLET_PATTERN = re.compile(r"^[\s]*[-•*]\s", re.MULTILINE)
_NUMBERED_PATTERN = re.compile(r"^[\s]*\d+[.)]\s", re.MULTILINE)
_MAX_BODY_LENGTH = 3000  # characters; well above expected output


def _check_structure(text: str) -> None:
    """Log warnings if the body violates structural expectations.

    Checks are intentionally soft — they warn, never raise.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if len(paragraphs) == 0:
        logger.warning("Structural check: body has 0 paragraphs.")
    elif len(paragraphs) > 5:
        logger.warning(
            "Structural check: body has %d paragraphs (expected ≤ 5).",
            len(paragraphs),
        )

    if _BULLET_PATTERN.search(text):
        logger.warning("Structural check: body appears to contain bullet points.")

    if _NUMBERED_PATTERN.search(text):
        logger.warning("Structural check: body appears to contain numbered lists.")

    if len(text) > _MAX_BODY_LENGTH:
        logger.warning(
            "Structural check: body length %d exceeds %d characters.",
            len(text),
            _MAX_BODY_LENGTH,
        )


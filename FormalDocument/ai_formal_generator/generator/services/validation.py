"""Input validation helpers for the AI service layer.

Centralises language checks, document-type validation, and empty-string guards.
"""

from __future__ import annotations

from typing import Literal, get_args

SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "hi")
Language = Literal["en", "hi"]
DocumentType = Literal["office", "circular", "policy"]

# Derived from the Literal for runtime validation
_VALID_DOCUMENT_TYPES: frozenset[str] = frozenset(get_args(DocumentType))


def validate_document_type(document_type: str) -> None:
    """Raise ``ValueError`` if *document_type* is not a known type.

    Accepts ``str`` rather than ``DocumentType`` so callers outside
    the type-checked boundary still get a clear error.
    """
    if document_type not in _VALID_DOCUMENT_TYPES:
        raise ValueError(
            f"Unsupported document_type '{document_type}'. "
            f"Must be one of: {tuple(sorted(_VALID_DOCUMENT_TYPES))}"
        )


def validate_inputs(language: str, **fields: str) -> None:
    """Validate language and one or more named string fields.

    Args:
        language: Must be one of :data:`SUPPORTED_LANGUAGES`.
        **fields: Keyword arguments of ``field_name=value`` to check for emptiness.

    Raises:
        ValueError: On the first failing check.
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. Must be one of: {SUPPORTED_LANGUAGES}"
        )
    for name, value in fields.items():
        if not (value or "").strip():
            raise ValueError(f"'{name}' cannot be empty.")


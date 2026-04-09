"""AI service package — public API re-exports.

Usage::

    from generator.services import generate_body, regenerate_body

    body = generate_body("office", topic="...", language="en")
"""

from .service import generate_body, regenerate_body, translate_subject_to_hindi  # noqa: F401
from .client import reset_client  # noqa: F401
from .validation import DocumentType, Language  # noqa: F401

__all__ = [
    "generate_body",
    "regenerate_body",
    "translate_subject_to_hindi",
    "reset_client",
    "DocumentType",
    "Language",
]


"""Shared prompt-layer utilities used by all document-type prompt builders.

Centralises the Language type alias re-export and helper functions
that were previously duplicated in every prompt file.
"""

from datetime import date

from langchain_core.prompts import PromptTemplate

from generator.services.validation import SUPPORTED_LANGUAGES, Language  # noqa: F401


def validate_language(language: str, *, document_type: str = "document") -> None:
    """Raise ``ValueError`` if *language* is not supported."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}' for {document_type} prompt. "
            f"Must be one of: {SUPPORTED_LANGUAGES}"
        )


def select_template(
    en_template: PromptTemplate,
    hi_template: PromptTemplate,
    language: str,
) -> PromptTemplate:
    """Return the correct template for *language*."""
    return hi_template if language == "hi" else en_template


def _require_non_empty(value: str | None, field_name: str) -> str:
    """Strip and validate a string field; raise ``ValueError`` if empty."""
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty.")
    return value


def build_generation(
    *,
    en_template: PromptTemplate,
    hi_template: PromptTemplate,
    prompt_version: str,
    topic: str,
    language: Language = "en",
    document_type: str = "document",
) -> str:
    """Shared builder for all generation prompts."""
    validate_language(language, document_type=document_type)
    topic = _require_non_empty(topic, "topic")

    return select_template(en_template, hi_template, language).format(
        topic=topic,
        version=prompt_version,
    )


def build_regeneration(
    *,
    en_template: PromptTemplate,
    hi_template: PromptTemplate,
    prompt_version: str,
    topic: str,
    previous_body: str,
    refinement_prompt: str,
    language: Language = "en",
    document_type: str = "document",
) -> str:
    """Shared builder for all regeneration prompts."""
    validate_language(language, document_type=document_type)
    topic = _require_non_empty(topic, "topic")
    previous_body = _require_non_empty(previous_body, "previous_body")
    refinement_prompt = _require_non_empty(refinement_prompt, "refinement_prompt")

    return select_template(en_template, hi_template, language).format(
        topic=topic,
        previous_body=previous_body,
        refinement_prompt=refinement_prompt,
        today=date.today().strftime("%d-%m-%Y"),
        version=prompt_version,
    )



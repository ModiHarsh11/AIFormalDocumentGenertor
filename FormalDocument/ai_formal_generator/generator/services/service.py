"""Public AI service API for FormalDocument generators (BISAG-N).

Public API
----------
generate_body(document_type, topic, language)                                     -> str
regenerate_body(document_type, topic, previous_body, refinement_prompt, language)  -> str
translate_subject_to_hindi(subject)                                               -> str
"""

import logging

from .client import get_client, MODEL_FALLBACK_CHAIN, GENERATION_CONFIG
from .registry import DOCUMENT_PROMPT_REGISTRY, PROMPT_VERSION_REGISTRY
from .sanitization import strip_markdown, validate_body
from .validation import (
    DocumentType,
    Language,
    validate_document_type,
    validate_inputs,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_quota_error(exc: Exception) -> bool:
    """Return True if *exc* looks like a quota / rate-limit error."""
    s = str(exc).lower()
    return (
        "quota" in s
        or "429" in s
        or "resource_exhausted" in s
        or ("rate" in s and "limit" in s)
        or "too many requests" in s
    )

def _is_unavailable_error(exc: Exception) -> bool:
    """Return True if *exc* looks like the model is unavailable / not found."""
    s = str(exc).lower()
    return (
        "not found" in s
        or "404" in s
        or "unavailable" in s
        or "503" in s
        or ("model" in s and "not" in s)
    )


# ---------------------------------------------------------------------------
# Core generation (private) — with automatic model fallback
# ---------------------------------------------------------------------------

def _generate(
    prompt: str,
    *,
    context: dict | None = None,
    sanitize_for_body: bool = True,
) -> str:
    """Call the Gemini API with automatic model fallback.

    Tries each model in ``MODEL_FALLBACK_CHAIN`` in order.
    Falls through to the next model on quota / unavailability errors.
    Raises :exc:`RuntimeError` only after every model is exhausted.
    """
    ctx = context or {}
    last_exc: Exception | None = None

    for model in MODEL_FALLBACK_CHAIN:
        try:
            logger.debug("Trying model %s", model, extra={"context": ctx})
            response = get_client().models.generate_content(
                model=model,
                contents=prompt,
                config=GENERATION_CONFIG,
            )
            if not response.candidates:
                raise RuntimeError(
                    "AI returned empty response (possibly blocked by safety filters)."
                )
            text = strip_markdown(response.text.strip())
            if sanitize_for_body:
                text = validate_body(text)
                if not text:
                    raise RuntimeError("AI returned invalid or empty body after validation.")
            elif not text:
                raise RuntimeError("AI returned empty response.")

            if model != MODEL_FALLBACK_CHAIN[0]:
                logger.info(
                    "Used fallback model %s (primary was unavailable/quota-exceeded).",
                    model,
                    extra={"context": ctx},
                )
            return text

        except RuntimeError:
            raise  # validation / empty-response errors — don't retry with another model

        except Exception as exc:
            exc_str = str(exc).lower()

            # API key errors are fatal — no point trying other models
            if "api_key" in exc_str or "api key" in exc_str or (
                "invalid" in exc_str and "key" in exc_str
            ):
                raise RuntimeError(
                    "Invalid API key. Please check your GEMINI_API_KEY in the .env file."
                )
            if "connection" in exc_str or "network" in exc_str or "timeout" in exc_str:
                raise RuntimeError(
                    "Network error reaching the AI service. "
                    "Please check your internet connection."
                )

            if _is_quota_error(exc) or _is_unavailable_error(exc):
                logger.warning(
                    "Model %s unavailable/quota-exceeded (%s), trying next model.",
                    model, exc, extra={"context": ctx},
                )
                last_exc = exc
                continue  # ← try the next model in the chain

            # Unknown error — log and propagate
            logger.exception(
                "Gemini API call failed on model %s.", model,
                extra={"context": ctx},
            )
            raise RuntimeError(f"AI generation failed: {exc}")

    # Every model in the chain was exhausted
    raise RuntimeError(
        "All AI models are currently quota-exceeded or unavailable. "
        "Please wait a few minutes and try again. "
        f"(Last error: {last_exc})"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_body(
    document_type: DocumentType,
    topic: str,
    language: Language = "en",
) -> str:
    """Generate the body for any supported document type.

    Routing is handled via :data:`DOCUMENT_PROMPT_REGISTRY`.

    Args:
        document_type: One of ``'office'``, ``'circular'``, ``'policy'``.
        topic:         Subject / topic of the document.
        language:      Output language — ``'en'`` (default) or ``'hi'``.
    """
    validate_document_type(document_type)
    validate_inputs(language, topic=topic)
    topic = topic.strip()

    prompt_builder = DOCUMENT_PROMPT_REGISTRY[document_type]["generate"]

    return _generate(
        prompt_builder(topic, language),
        context={
            "fn": "generate_body",
            "document_type": document_type,
            "prompt_version": PROMPT_VERSION_REGISTRY.get(document_type, "unknown"),
            "language": language,
            "topic_length": len(topic),
        },
    )


def regenerate_body(
    document_type: DocumentType,
    topic: str,
    previous_body: str,
    refinement_prompt: str,
    language: Language = "en",
) -> str:
    """Refine a previously generated document body for any supported type.

    Routing is handled via :data:`DOCUMENT_PROMPT_REGISTRY`.

    Args:
        document_type:     One of ``'office'``, ``'circular'``, ``'policy'``.
        topic:             The original topic / subject used in the first call.
        previous_body:     The body text that was shown to the user.
        refinement_prompt: The user's feedback / change request.
        language:          Output language — ``'en'`` (default) or ``'hi'``.
    """
    validate_document_type(document_type)
    validate_inputs(
        language,
        topic=topic,
        previous_body=previous_body,
        refinement_prompt=refinement_prompt,
    )
    topic = topic.strip()
    previous_body = previous_body.strip()
    refinement_prompt = refinement_prompt.strip()

    prompt_builder = DOCUMENT_PROMPT_REGISTRY[document_type]["regenerate"]

    return _generate(
        prompt_builder(
            topic=topic,
            previous_body=previous_body,
            refinement_prompt=refinement_prompt,
            language=language,
        ),
        context={
            "fn": "regenerate_body",
            "document_type": document_type,
            "prompt_version": PROMPT_VERSION_REGISTRY.get(document_type, "unknown"),
            "language": language,
            "topic_length": len(topic),
            "refinement_length": len(refinement_prompt),
        },
    )


def translate_subject_to_hindi(subject: str) -> str:
    """Translate a short subject line to formal Hindi."""
    validate_inputs("hi", subject=subject)
    subject = subject.strip()

    prompt = (
        "Translate the following official document subject to Hindi.\n"
        "Rules:\n"
        "1) Return only the translated subject line.\n"
        "2) Do not add labels like 'विषय' or extra punctuation.\n"
        "3) Keep names, acronyms, and codes intact.\n\n"
        f"Subject: {subject}"
    )

    return _generate(
        prompt,
        context={
            "fn": "translate_subject_to_hindi",
            "subject_length": len(subject),
        },
        sanitize_for_body=False,
    )


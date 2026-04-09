"""Lazy Gemini API client initialisation and caching.

NOTE: In multi-worker environments (e.g. Gunicorn), each worker holds its
own _client instance.  reset_client() only affects the current process.
"""

from django.conf import settings
from google import genai
from google.genai import types as genai_types

# ---------------------------------------------------------------------------
# Model fallback chain
# ---------------------------------------------------------------------------
# Models are tried in order.  If the primary is quota-exhausted or
# unavailable, the next one is attempted automatically.
# Override the primary via settings.LLM_MODEL; the rest of the chain
# is always appended as a safety net.
_PRIMARY_MODEL: str = getattr(settings, "LLM_MODEL", "gemini-2.5-flash-lite")

# Full ordered fallback list (primary first, then backups)
MODEL_FALLBACK_CHAIN: list[str] = [
    _PRIMARY_MODEL,
    # Remove duplicates while preserving order
    *[m for m in [
        "gemini-2.5-flash-lite",
        "gemini-2-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash-exp",
        "gemma-3-12b-it",
    ] if m != _PRIMARY_MODEL],
]


# Read-only config shared across all generate_content calls.
GENERATION_CONFIG = genai_types.GenerateContentConfig(
    temperature=0.3,
    max_output_tokens=1024,
)

# --- Lazy client singleton ---
_client: genai.Client | None = None


def get_client() -> genai.Client:
    """Lazily initialise and cache the Gemini API client."""
    global _client
    if _client is None:
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Set it in your environment or Django settings."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def reset_client() -> None:
    """Reset cached client.  Useful for testing or API key rotation."""
    global _client
    _client = None


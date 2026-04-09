"""Prompt registry — maps document types to their prompt builder functions.

Adding a new document type requires:
1. A new prompt file in ``generator/prompts/``
2. One entry in each registry below.

No new service functions needed.
"""

from typing import Callable

from generator.prompts.office_order import (
    build_generation_prompt as build_office_generation_prompt,
    build_regeneration_prompt as build_office_regeneration_prompt,
    PROMPT_VERSION as OFFICE_PROMPT_VERSION,
)
from generator.prompts.circular import (
    build_generation_prompt as build_circular_generation_prompt,
    build_regeneration_prompt as build_circular_regeneration_prompt,
    PROMPT_VERSION as CIRCULAR_PROMPT_VERSION,
)
from generator.prompts.policy import (
    build_generation_prompt as build_policy_generation_prompt,
    build_regeneration_prompt as build_policy_regeneration_prompt,
    PROMPT_VERSION as POLICY_PROMPT_VERSION,
)

from .validation import DocumentType

# Maps document_type → action → prompt builder function.
DOCUMENT_PROMPT_REGISTRY: dict[DocumentType, dict[str, Callable[..., str]]] = {
    "office": {
        "generate": build_office_generation_prompt,
        "regenerate": build_office_regeneration_prompt,
    },
    "circular": {
        "generate": build_circular_generation_prompt,
        "regenerate": build_circular_regeneration_prompt,
    },
    "policy": {
        "generate": build_policy_generation_prompt,
        "regenerate": build_policy_regeneration_prompt,
    },
}

# Maps document_type → prompt version string for structured logging.
PROMPT_VERSION_REGISTRY: dict[DocumentType, str] = {
    "office": OFFICE_PROMPT_VERSION,
    "circular": CIRCULAR_PROMPT_VERSION,
    "policy": POLICY_PROMPT_VERSION,
}


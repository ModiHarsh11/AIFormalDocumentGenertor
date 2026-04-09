# 🛡️ Phase 7 — Prompt Hardening Across All Document Types

## What This Phase Covers

Phases 1–6 built the layered architecture, SDK migration, prompt hardening, output validation, prompt abstraction, and regeneration symmetry — all **primarily for Office Orders**.

Phase 7 applies every improvement uniformly to **all three document types**: Office Order, Circular, and Policy.

---

## The Problem

Before this phase, `circular.py` and `policy.py` existed but were inconsistent with `office_order.py`:

| Gap | Detail |
|-----|--------|
| No module docstring | Neither file had a public API docstring |
| No `Language` type alias | `language` param was typed as plain `str` |
| No `_validate_language` docstring | Private helpers lacked documentation |
| No `_select_template` docstring | Same |
| No `build_*` docstrings | Public builder functions were undocumented |
| No input validation | `topic`, `previous_body`, `refinement_prompt` not validated for emptiness |
| No default `language` param | Callers that omitted `language` got `TypeError` |
| Inconsistent error messages | `ValueError` messages didn't include the invalid value or allowed set |

---

## Changes Applied to All Three Prompt Files

Each file (`office_order.py`, `circular.py`, `policy.py`) now has:

```python
"""Prompt builder for Government {DocType} documents (BISAG-N).

Public API
----------
build_generation_prompt(topic, language)  -> str
build_regeneration_prompt(topic, previous_body, refinement_prompt, language) -> str
"""

from datetime import date
from typing import Literal

from langchain.prompts import PromptTemplate

PROMPT_VERSION = "{DocType}_v1"
SUPPORTED_LANGUAGES = ("en", "hi")
Language = Literal["en", "hi"]
```

### Private helpers (consistent across all files)

```python
def _validate_language(language: str) -> None:
    """Raise ValueError if *language* is not supported."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}' for {DocType} prompt. "
            f"Must be one of: {SUPPORTED_LANGUAGES}"
        )

def _select_template(en_template, hi_template, language) -> PromptTemplate:
    """Return the correct template for *language*."""
    return hi_template if language == "hi" else en_template
```

### Public builders (consistent across all files)

```python
def build_generation_prompt(topic: str, language: Language = "en") -> str:
    """Return a formatted generation prompt for a {DocType} body."""
    _validate_language(language)
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("topic cannot be empty.")
    template = _select_template(GENERATION_TEMPLATE_EN, GENERATION_TEMPLATE_HI, language)
    return template.format(topic=topic, version=PROMPT_VERSION)

def build_regeneration_prompt(
        topic, previous_body, refinement_prompt, language: Language = "en"
) -> str:
    """Return a formatted regeneration prompt for a {DocType} body."""
    _validate_language(language)
    # validate + strip all three string inputs
    ...
```

---

## Symmetry Verification

| Feature | `office_order.py` | `circular.py` | `policy.py` |
|---------|-------------------|---------------|-------------|
| Module docstring | ✅ | ✅ | ✅ |
| `Language = Literal["en", "hi"]` | ✅ | ✅ | ✅ |
| `_validate_language` with docstring | ✅ | ✅ | ✅ |
| `_select_template` with docstring | ✅ | ✅ | ✅ |
| `build_generation_prompt` with docstring | ✅ | ✅ | ✅ |
| `build_regeneration_prompt` with docstring | ✅ | ✅ | ✅ |
| Input validation (strip + empty-check) | ✅ | ✅ | ✅ |
| Default `language="en"` on both builders | ✅ | ✅ | ✅ |
| Descriptive `ValueError` messages | ✅ | ✅ | ✅ |

All three files are now character-for-character identical in structure, differing only in template content and `PROMPT_VERSION` value.

---

## Outcome

✅ All prompt files have consistent structure  
✅ All prompt files validate inputs defensively  
✅ All prompt files are fully documented  
✅ Adding a fourth document type now has a clear, copy-and-adapt pattern  

